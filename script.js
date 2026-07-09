const leadForm = document.querySelector("#leadForm");
const leadMessage = document.querySelector("#leadMessage");

function setMessage(type, text) {
  if (!leadMessage) return;
  const isSuccess = type === "success";
  leadMessage.className = [
    "mt-4 rounded-lg p-4 text-sm font-bold",
    isSuccess ? "bg-emerald-50 text-emerald-800" : "bg-red-50 text-red-800"
  ].join(" ");
  leadMessage.textContent = text;
}

function formToLead(form) {
  const data = new FormData(form);
  return {
    name: data.get("name"),
    email: data.get("email"),
    phone: data.get("phone"),
    goal: data.get("goal"),
    scoreRange: data.get("scoreRange"),
    planInterest: data.get("planInterest"),
    preferredContact: data.get("preferredContact"),
    notes: data.get("notes"),
    companyWebsite: data.get("companyWebsite"),
    source: "credit-vivo-homepage"
  };
}

leadForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const submitButton = leadForm.querySelector("button[type='submit']");
  submitButton.disabled = true;
  submitButton.textContent = "Saving review request...";
  setMessage("success", "Saving your request...");

  try {
    const response = await fetch("/api/leads", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json"
      },
      body: JSON.stringify(formToLead(leadForm))
    });

    const data = await response.json();
    if (!response.ok || !data.ok) {
      throw new Error((data.errors || ["Please check the form and try again."]).join(" "));
    }

    leadForm.reset();
    setMessage("success", "Request received. Credit Vivo will review your path and follow up with next steps.");
  } catch (error) {
    setMessage("error", error.message || "Unable to save this request. Please try again.");
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Start free review";
  }
});
