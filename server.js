const { app } = require("./src/config");
const { createServer } = require("./src/app");

const server = createServer();

server.listen(app.port, app.host, () => {
  console.log(`Credit Vivo ${app.version} running at http://${app.host}:${app.port}`);
});
