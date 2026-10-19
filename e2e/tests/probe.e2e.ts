import { test } from '@e2e-dev/mobile';
import { expect } from 'e2e';

test('opens the diagnostics screen', async ({ app, screen }) => {
  await app.open();
  await expect(screen.getByTestId('probe.run')).toBeVisible();
  await expect(screen.getByTestId('probe.report')).toBeVisible();
});

test('runs the probe and displays a report', async ({ app, screen }) => {
  await app.open();
  await screen.getByTestId('probe.run').tap();
  // Simulator GPU capabilities are NOT evidence of iPad mini A17 Pro compatibility.
  await expect(screen.getByTestId('probe.report')).toContainText('Metal');
  await expect(screen.getByTestId('probe.share')).toBeVisible();
});
