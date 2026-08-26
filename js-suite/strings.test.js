const { reverse, isPalindrome } = require("./strings");

describe("strings", () => {
  test("reverse: basic word", () => {
    expect(reverse("hello")).toBe("olleh");
  });

  test("reverse: empty string", () => {
    expect(reverse("")).toBe("");
  });

  test("isPalindrome: true case", () => {
    expect(isPalindrome("racecar")).toBe(true);
  });

  test("isPalindrome: false case", () => {
    expect(isPalindrome("hello")).toBe(false);
  });

  test("isPalindrome: ignores case and punctuation", () => {
    expect(isPalindrome("A man, a plan, a canal: Panama")).toBe(true);
  });
});
