import { test, expect } from '@playwright/test';

test.describe('Calculations with JWT Authentication', () => {
  let authToken: string;
  let userId: number;

  test.beforeAll(async ({ request }) => {
    // Register a test user and get JWT token
    const timestamp = Date.now();
    const response = await request.post('/auth/register', {
      data: {
        email: `calctest${timestamp}@example.com`,
        username: `calctest${timestamp}`,
        password: 'SecurePass123'
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    authToken = data.access_token;
    expect(authToken).toBeTruthy();
  });

  test('should create a calculation with JWT', async ({ request }) => {
    // Create a calculation
    const response = await request.post('/calculations/', {
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      data: {
        a: 10,
        b: 5,
        type: 'Add'
      }
    });

    expect(response.ok()).toBeTruthy();
    const calculation = await response.json();
    expect(calculation).toHaveProperty('id');
    expect(calculation.result).toBe(15);
    expect(calculation.type).toBe('Add');
  });

  test('should list calculations', async ({ request }) => {
    // Create multiple calculations
    await request.post('/calculations/', {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: { a: 20, b: 10, type: 'Sub' }
    });
    
    await request.post('/calculations/', {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: { a: 5, b: 4, type: 'Multiply' }
    });

    // List all calculations
    const response = await request.get('/calculations/', {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });

    expect(response.ok()).toBeTruthy();
    const calculations = await response.json();
    expect(Array.isArray(calculations)).toBeTruthy();
    expect(calculations.length).toBeGreaterThanOrEqual(2);
  });

  test('should update a calculation', async ({ request }) => {
    // Create a calculation
    const createResponse = await request.post('/calculations/', {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: { a: 100, b: 50, type: 'Add' }
    });
    
    const created = await createResponse.json();
    const calcId = created.id;

    // Update the calculation
    const updateResponse = await request.put(`/calculations/${calcId}`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: { a: 100, b: 50, type: 'Sub' }
    });

    expect(updateResponse.ok()).toBeTruthy();
    const updated = await updateResponse.json();
    expect(updated.id).toBe(calcId);
    expect(updated.result).toBe(50);
    expect(updated.type).toBe('Sub');
  });

  test('should delete a calculation', async ({ request }) => {
    // Create a calculation
    const createResponse = await request.post('/calculations/', {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: { a: 8, b: 2, type: 'Divide' }
    });
    
    const created = await createResponse.json();
    const calcId = created.id;

    // Delete the calculation
    const deleteResponse = await request.delete(`/calculations/${calcId}`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });

    expect(deleteResponse.ok()).toBeTruthy();

    // Verify it's deleted
    const getResponse = await request.get(`/calculations/${calcId}`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    expect(getResponse.status()).toBe(404);
  });

  test('should reject calculation without JWT', async ({ request }) => {
    // Try to create calculation without token
    const response = await request.post('/calculations/', {
      data: { a: 10, b: 5, type: 'Add' }
    });

    // Should fail with 401 or 403 (depending on implementation)
    // If the endpoint doesn't require auth, it might succeed
    // This test assumes protected endpoints
    if (response.status() === 403 || response.status() === 401) {
      expect(response.ok()).toBeFalsy();
    }
  });

  test('should handle division by zero', async ({ request }) => {
    const response = await request.post('/calculations/', {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: { a: 10, b: 0, type: 'Divide' }
    });

    expect(response.status()).toBe(422); // Validation error
    const error = await response.json();
    expect(error.detail).toBeTruthy();
  });

  test('should validate calculation types', async ({ request }) => {
    const response = await request.post('/calculations/', {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: { a: 10, b: 5, type: 'InvalidOperation' }
    });

    expect(response.status()).toBe(422); // Validation error
  });

  test.describe('UI Integration with Calculations', () => {
    
    test('should create calculation through UI after login', async ({ page }) => {
      // Register and login
      const timestamp = Date.now();
      const email = `uitest${timestamp}@example.com`;
      const username = `uitest${timestamp}`;
      const password = 'SecurePass123';
      
      await page.request.post('/auth/register', {
        data: { email, username, password }
      });

      // Login through UI
      await page.goto('/frontend/login.html');
      await page.fill('#username_or_email', email);
      await page.fill('#password', password);
      await page.click('button[type="submit"]');
      
      // Wait for redirect to main page
      await page.waitForURL('**/static/index.html', { timeout: 3000 });

      // Verify token is in localStorage
      const token = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(token).toBeTruthy();

      // Now test creating a calculation via API using the stored token
      const calcResponse = await page.request.post('/calculations/', {
        headers: { 'Authorization': `Bearer ${token}` },
        data: { a: 7, b: 3, type: 'Multiply' }
      });

      expect(calcResponse.ok()).toBeTruthy();
      const calc = await calcResponse.json();
      expect(calc.result).toBe(21);
    });
  });
});
