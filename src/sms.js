const { twilio } = require("./config");

function smsStatus() {
  const configured = Boolean(
    twilio.accountSid
    && twilio.apiKey
    && twilio.apiSecret
    && twilio.fromNumber
    && twilio.founderPhone
  );

  return {
    configured,
    provider: "twilio",
    fromNumber: twilio.fromNumber ? twilio.fromNumber.replace(/\d(?=\d{4})/g, "*") : "",
    founderPhone: twilio.founderPhone ? twilio.founderPhone.replace(/\d(?=\d{4})/g, "*") : ""
  };
}

async function sendFounderSms(message) {
  if (!smsStatus().configured) {
    return { ok: false, errors: ["Twilio SMS is not configured."] };
  }

  const body = new URLSearchParams({
    To: twilio.founderPhone,
    From: twilio.fromNumber,
    Body: String(message || "").slice(0, 600)
  });

  const auth = Buffer.from(`${twilio.apiKey}:${twilio.apiSecret}`).toString("base64");
  const response = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${twilio.accountSid}/Messages.json`, {
    method: "POST",
    headers: {
      Authorization: `Basic ${auth}`,
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body
  });

  const data = await response.json();
  if (!response.ok) {
    if (data.code === 572006) {
      return {
        ok: false,
        errors: ["Twilio trial sent from Console, but API SMS requires an upgraded account or approved Twilio template."],
        code: data.code,
        status: response.status
      };
    }
    return {
      ok: false,
      errors: [data.message || "Twilio SMS failed."],
      code: data.code || null,
      status: response.status
    };
  }

  return {
    ok: true,
    sid: data.sid,
    status: data.status,
    to: smsStatus().founderPhone,
    from: smsStatus().fromNumber
  };
}

module.exports = { smsStatus, sendFounderSms };
