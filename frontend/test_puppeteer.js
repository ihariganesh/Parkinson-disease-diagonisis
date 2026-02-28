const { chromium } = require('puppeteer');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  await page.goto('http://localhost:5174/longitudinal', { waitUntil: 'networkidle0' });
  
  await browser.close();
})();
