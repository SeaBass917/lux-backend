import { render, screen } from "@testing-library/react";
import TopNavBar from "./TopNavBar";

test("Tab Title Text Formatting", () => {
  render(<TopNavBar />);
  const tabEles = document.getElementsByClassName("NavTab");
  expect(tabEles).toBeDefined();

  for (let tabEle of tabEles) {
    const text = tabEle.textContent;
    // Text must be
    //   - Alphabetical
    //   - Title Case
    //   - Between [3,6] character long
    expect(text).toMatch(/^[A-Z][a-z]{2,5}$/);
  }
});
