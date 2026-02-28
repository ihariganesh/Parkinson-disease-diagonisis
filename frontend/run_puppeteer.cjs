const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  console.log("Launching browser...");
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.type(), msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  console.log("Navigating to localhost:5173...");
  await page.goto('http://localhost:5173/longitudinal', { waitUntil: 'load' });
  
  await page.waitForTimeout(3000);
  console.log("Done waiting.");
  const content = await page.content();
  console.log("CONTENT LENGTH", content.length);
  
  await browser.close();
})();
