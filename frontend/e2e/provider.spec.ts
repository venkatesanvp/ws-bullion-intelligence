import { expect, test } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../../', import.meta.url));
const python = fileURLToPath(new URL(process.platform === 'win32' ? '../../.venv/Scripts/python.exe' : '../../.venv/bin/python', import.meta.url));

test('synthetic one-year provider import feeds charts indicators and both metal comparisons', async ({ page }) => {
  test.setTimeout(90000);
  if (!process.env.TEST_DATABASE_URL || !process.env.TEST_APP_TOKEN) throw new Error('Explicit disposable test database required');
  const seeded = JSON.parse(execFileSync(python, ['-m', 'tests.seed_provider_browser'], {
    cwd: root, env: { ...process.env, PYTHONPATH: 'backend' }, encoding: 'utf8'
  })) as { source_id: string; instruments: { id: string; symbol: string }[]; data_class: string };
  expect(seeded.data_class).toBe('SYNTHETIC_TEST');
  const external: string[] = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (['http:', 'https:'].includes(url.protocol) && !['http://127.0.0.1:5173', 'http://127.0.0.1:8001'].includes(url.origin)) external.push(request.url());
  });
  await page.goto('/');
  await page.getByLabel('Local application token').fill(process.env.TEST_APP_TOKEN);
  await page.getByRole('button', { name: /Open Bullion Workspace/ }).click();
  await page.getByRole('button', { name: 'Research dashboard', exact: true }).click();
  await page.getByLabel('ETF listing').selectOption(seeded.instruments[0].id);
  await page.getByLabel('Data source').selectOption(seeded.source_id);
  await page.getByRole('combobox', { name: 'Price basis', exact: true }).selectOption('PROVIDER_ADJUSTED');
  for (const method of ['SMA', 'EMA', 'RSI']) {
    await page.getByRole('checkbox', { name: method === 'RSI' ? 'Show Wilder RSI' : 'Show ' + method, exact: true }).check();
    await page.getByLabel(method + ' lookback', { exact: true }).fill(method === 'SMA' ? '200' : method === 'EMA' ? '37' : '14');
  }
  await page.getByRole('button', { name: 'Apply research settings' }).click();
  await page.getByLabel('Chart engine',{exact:true}).selectOption('plotly');
  await expect(page.getByRole('img', { name: 'TATAGOLD price chart', exact: true }).locator('svg.main-svg').first()).toBeVisible();
  await expect(page.getByRole('img', { name: 'RSI / 1d', exact: true }).locator('svg.main-svg').first()).toBeVisible();
  await expect(page.getByText(/TIMESTAMP CONTRACT UNVERIFIED/).first()).toBeVisible();
  await expect(page.getByRole('table', { name: 'Exact prices and server-calculated indicator values' })).toBeVisible();
  await page.getByRole('button', { name: 'ETF comparisons', exact: true }).click();
  for (const pair of [[0, 2], [1, 3]]) {
    for (let i = 0; i < 2; i++) {
      await page.getByRole('combobox', { name: 'Comparison ETF ' + (i + 1), exact: true }).selectOption(seeded.instruments[pair[i]].id);
      await page.getByRole('combobox', { name: 'Comparison source ' + (i + 1), exact: true }).selectOption(seeded.source_id);
      await page.getByRole('combobox', { name: 'Comparison basis ' + (i + 1), exact: true }).selectOption('PROVIDER_ADJUSTED');
    }
    await page.getByLabel('Comparison from', { exact: true }).fill('2025-11-02');
    await page.getByLabel('Comparison through', { exact: true }).fill('2026-11-02');
    await page.getByRole('button', { name: 'Compare prices', exact: true }).click();
    await expect(page.getByRole('img', { name: 'Price-only common-date comparison', exact: true }).locator('.scatterlayer .trace')).toHaveCount(2);
    await expect(page.getByText(/Price-only change is not total return/)).toBeVisible();
  }
  expect(external).toEqual([]);
});
