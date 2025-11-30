import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test.describe('Registration', () => {
    
    test('should successfully register a new user', async ({ page }) => {
      // Navigate to register page
      await page.goto('/frontend/register.html');
      
      // Generate unique credentials
      const timestamp = Date.now();
      const email = `testuser${timestamp}@example.com`;
      const username = `testuser${timestamp}`;
      const password = 'SecurePass123';
      
      // Fill in the form
      await page.fill('#email', email);
      await page.fill('#username', username);
      await page.fill('#password', password);
      await page.fill('#confirmPassword', password);
      
      // Submit the form
      await page.click('button[type="submit"]');
      
      // Wait for success message
      await expect(page.locator('#successMessage')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('#successMessage')).toContainText('Account created successfully');
      
      // Verify token is stored in localStorage
      const token = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(token).toBeTruthy();
      expect(token).toMatch(/^[\w-]+\.[\w-]+\.[\w-]+$/); // JWT format check
      
      // Wait for redirect
      await page.waitForURL('**/static/index.html', { timeout: 3000 });
    });

    test('should show client-side validation for short password', async ({ page }) => {
      await page.goto('/frontend/register.html');
      
      // Fill in form with short password
      await page.fill('#email', 'test@example.com');
      await page.fill('#username', 'testuser');
      await page.fill('#password', 'short');
      await page.fill('#confirmPassword', 'short');
      
      // Trigger validation by blurring password field
      await page.click('#username'); // Click away from password
      
      // Check that error message appears
      const passwordError = page.locator('#passwordError');
      await expect(passwordError).toBeVisible();
      await expect(passwordError).toContainText('at least 8 characters');
    });

    test('should show error for mismatched passwords', async ({ page }) => {
      await page.goto('/frontend/register.html');
      
      // Fill in form with mismatched passwords
      await page.fill('#email', 'test@example.com');
      await page.fill('#username', 'testuser');
      await page.fill('#password', 'SecurePass123');
      await page.fill('#confirmPassword', 'DifferentPass123');
      
      // Blur the confirm password field to trigger validation
      await page.click('#email');
      
      // Check that error message appears
      const confirmError = page.locator('#confirmError');
      await expect(confirmError).toBeVisible();
      await expect(confirmError).toContainText('do not match');
    });

    test('should show error for invalid email format', async ({ page }) => {
      await page.goto('/frontend/register.html');
      
      // Fill in form with invalid email
      await page.fill('#email', 'invalid-email');
      await page.fill('#username', 'testuser');
      
      // Blur email field to trigger validation
      await page.click('#username');
      
      // Check that error message appears
      const emailError = page.locator('#emailError');
      await expect(emailError).toBeVisible();
    });

    test('should show server error for duplicate email', async ({ page }) => {
      // First registration
      const email = `duplicate${Date.now()}@example.com`;
      const username = `duplicate${Date.now()}`;
      const password = 'SecurePass123';
      
      await page.goto('/frontend/register.html');
      await page.fill('#email', email);
      await page.fill('#username', username);
      await page.fill('#password', password);
      await page.fill('#confirmPassword', password);
      await page.click('button[type="submit"]');
      
      // Wait for first registration to complete
      await expect(page.locator('#successMessage')).toBeVisible({ timeout: 5000 });
      
      // Clear localStorage and navigate back
      await page.evaluate(() => localStorage.clear());
      await page.goto('/frontend/register.html');
      
      // Try to register again with same email
      await page.fill('#email', email);
      await page.fill('#username', `different${username}`);
      await page.fill('#password', password);
      await page.fill('#confirmPassword', password);
      await page.click('button[type="submit"]');
      
      // Wait for error to appear
      await page.waitForTimeout(1000);
      
      // Check that error is shown
      const emailError = page.locator('#emailError');
      await expect(emailError).toBeVisible();
      await expect(emailError).toContainText(/already/i);
    });
  });

  test.describe('Login', () => {
    
    test('should successfully login with valid credentials', async ({ page, context }) => {
      // First, register a user
      const timestamp = Date.now();
      const email = `logintest${timestamp}@example.com`;
      const username = `logintest${timestamp}`;
      const password = 'SecurePass123';
      
      // Register via API
      const response = await page.request.post('/auth/register', {
        data: {
          email,
          username,
          password
        }
      });
      expect(response.ok()).toBeTruthy();
      
      // Clear any stored tokens
      await page.goto('/');
      await page.evaluate(() => localStorage.clear());
      
      // Now test login
      await page.goto('/frontend/login.html');
      
      // Fill in login form with email
      await page.fill('#username_or_email', email);
      await page.fill('#password', password);
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Wait for success message
      await expect(page.locator('#successMessage')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('#successMessage')).toContainText('Login successful');
      
      // Verify token is stored
      const token = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(token).toBeTruthy();
      
      // Wait for redirect
      await page.waitForURL('**/static/index.html', { timeout: 3000 });
    });

    test('should successfully login with username', async ({ page }) => {
      // Register a user first
      const timestamp = Date.now();
      const email = `logintest2${timestamp}@example.com`;
      const username = `logintest2${timestamp}`;
      const password = 'SecurePass123';
      
      await page.request.post('/auth/register', {
        data: { email, username, password }
      });
      
      // Clear localStorage
      await page.goto('/');
      await page.evaluate(() => localStorage.clear());
      
      // Login with username
      await page.goto('/frontend/login.html');
      await page.fill('#username_or_email', username);
      await page.fill('#password', password);
      await page.click('button[type="submit"]');
      
      // Verify success
      await expect(page.locator('#successMessage')).toBeVisible({ timeout: 5000 });
      const token = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(token).toBeTruthy();
    });

    test('should show error for invalid credentials', async ({ page }) => {
      await page.goto('/frontend/login.html');
      
      // Try to login with non-existent user
      await page.fill('#username_or_email', 'nonexistent@example.com');
      await page.fill('#password', 'WrongPassword123');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Wait for error message
      await expect(page.locator('#errorMessage')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('#errorMessage')).toContainText(/incorrect/i);
      
      // Verify no token is stored
      const token = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(token).toBeNull();
    });

    test('should show error for wrong password', async ({ page }) => {
      // Register a user
      const timestamp = Date.now();
      const email = `wrongpw${timestamp}@example.com`;
      const username = `wrongpw${timestamp}`;
      const password = 'CorrectPass123';
      
      await page.request.post('/auth/register', {
        data: { email, username, password }
      });
      
      // Try to login with wrong password
      await page.goto('/frontend/login.html');
      await page.fill('#username_or_email', email);
      await page.fill('#password', 'WrongPassword123');
      await page.click('button[type="submit"]');
      
      // Verify error message
      await expect(page.locator('#errorMessage')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('#errorMessage')).toContainText(/incorrect/i);
    });

    test('should validate empty fields', async ({ page }) => {
      await page.goto('/frontend/login.html');
      
      // Try to submit with empty fields
      await page.click('button[type="submit"]');
      
      // Error message should appear
      await expect(page.locator('#errorMessage')).toBeVisible({ timeout: 2000 });
      await expect(page.locator('#errorMessage')).toContainText(/email\/username and password/i);
    });
  });
});
