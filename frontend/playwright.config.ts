import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'node:url';

const python = fileURLToPath(new URL(
  process.platform === 'win32' ? '../.venv/Scripts/python.exe' : '../.venv/bin/python',
  import.meta.url
));

const testUrl = process.env.TEST_DATABASE_URL;
if (testUrl && !/^postgresql\+psycopg:\/\/[^/]+@(127\.0\.0\.1|localhost):\d+\/[^/?]+_test$/.test(testUrl)) {
  throw new Error('Browser tests require an explicit local disposable *_test database.');
}
export default defineConfig({
  testDir: './e2e', fullyParallel: false, workers: 1, retries: 0,
  reporter: [['list'], ['html', { open: 'never' }], ['junit', { outputFile: '../artifacts/browser-tests.xml' }]],
  use: { baseURL: 'http://127.0.0.1:15184', trace: 'retain-on-failure' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    { command: `"${python}" -m uvicorn app.main:app --host 127.0.0.1 --port 18011 --no-access-log`,
      cwd: '.', url: 'http://127.0.0.1:18011/api/v1/health/live', timeout: 30_000,
      env: { PYTHONPATH: '../backend', DATABASE_URL: testUrl || '', LOCAL_APP_TOKEN: process.env.TEST_APP_TOKEN || '', ALLOWED_ORIGINS: 'http://127.0.0.1:15184' }, reuseExistingServer: false },
    { command: `"${python}" -m uvicorn tests.session_browser_app:app --host 127.0.0.1 --port 18012 --no-access-log`,
      cwd: '.', url: 'http://127.0.0.1:18012/api/v1/health/live', timeout: 30_000,
      env: { PYTHONPATH: '../backend', TEST_DATABASE_URL: testUrl || '', DATABASE_URL: testUrl || '', LOCAL_APP_TOKEN: process.env.TEST_APP_TOKEN || '', ALLOWED_ORIGINS: 'http://127.0.0.1:15184' }, reuseExistingServer: false },
    { command: 'npm run dev -- --strictPort --port 15184' , url: 'http://127.0.0.1:15184',
      env: { VITE_API_ROOT: 'http://127.0.0.1:18011/api/v1' }, reuseExistingServer: false }
  ]
});
