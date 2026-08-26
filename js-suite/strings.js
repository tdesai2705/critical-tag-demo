function reverse(str) {
  return str.split("").reverse().join("");
}

function isPalindrome(str) {
  const normalized = str.toLowerCase().replace(/[^a-z0-9]/g, "");
  return normalized === reverse(normalized);
}

module.exports = { reverse, isPalindrome };
