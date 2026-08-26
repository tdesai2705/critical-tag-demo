const { add, multiply, divide } = require("./math");

describe("math", () => {
  test("add: positive numbers", () => {
    expect(add(2, 3)).toBe(5);
  });

  test("add: negative numbers", () => {
    expect(add(-2, -3)).toBe(-5);
  });

  test("multiply: basic", () => {
    expect(multiply(4, 5)).toBe(20);
  });

  test("multiply: by zero", () => {
    expect(multiply(4, 0)).toBe(0);
  });

  test("divide: basic", () => {
    expect(divide(10, 2)).toBe(5);
  });

  test("divide: by zero throws", () => {
    expect(() => divide(10, 0)).toThrow("cannot divide by zero");
  });
});
