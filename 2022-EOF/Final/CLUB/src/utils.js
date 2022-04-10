const crypto = require("crypto");

module.exports = {
  sha256(str) {
    if (typeof str !== "string") {
      return undefined;
    }
    const hash = crypto.createHash("sha256");
    hash.update(str);
    return hash.digest("hex");
  },
  isNumberStr(x) {
    if (typeof x !== "string") {
      return false;
    }
    return String(Number(x)) == x;
  },
  isColorStr(x) {
    if (typeof x !== "string") {
      return false;
    }
    return /^#[a-f0-9]{3}([a-f0-9]{3})?$/.test(x);
  },
};
