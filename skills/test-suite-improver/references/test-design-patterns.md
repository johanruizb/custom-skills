# Test Design Patterns by Framework

Framework-specific patterns for writing good tests. Consult during Phase 5 (research) and Phase 8 (generation). This file provides baseline patterns; always cross-reference with the latest official docs for the detected version.

---

## Python — pytest

### Structure
```python
# tests/test_user_service.py
import pytest
from myapp.services import UserService
from myapp.models import User

class TestUserService:
    """Group related tests in a class for organization."""

    def test_creates_user_with_valid_data(self, db):
        service = UserService(db)
        user = service.create(email="test@example.com", name="Test")
        assert user.id is not None
        assert user.email == "test@example.com"
        assert User.query.count() == 1

    def test_rejects_duplicate_email(self, db):
        service = UserService(db)
        service.create(email="dup@example.com", name="First")
        with pytest.raises(ValueError, match="already exists"):
            service.create(email="dup@example.com", name="Second")

    def test_returns_none_for_unknown_user(self, db):
        service = UserService(db)
        assert service.get_by_id(99999) is None
```

### Fixtures
```python
# tests/conftest.py
import pytest
from myapp.app import create_app
from myapp.db import db as _db

@pytest.fixture(scope="session")
def app():
    app = create_app(testing=True)
    with app.app_context():
        yield app

@pytest.fixture(scope="function")
def db(app):
    _db.create_all()
    yield _db
    _db.session.rollback()
    _db.drop_all()

@pytest.fixture
def user_factory(db):
    from factories import UserFactory
    return UserFactory
```

### Parametrized tests
```python
@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("invalid", False),
    ("", False),
    (None, False),
    ("user@.com", False),
])
def test_validates_email(email, valid):
    assert validate_email(email) == valid
```

### Mocking external boundaries only
```python
from unittest.mock import patch, MagicMock

def test_sends_email_on_signup(self, db):
    service = UserService(db)
    with patch("myapp.services.EmailClient.send") as mock_send:
        service.create(email="test@example.com", name="Test")
        mock_send.assert_called_once()
        assert "test@example.com" in mock_send.call_args[0][0]
```

### Async tests
```python
import pytest

@pytest.mark.asyncio
async def test_fetches_user_async():
    result = await fetch_user(1)
    assert result["id"] == 1
```

### Best practices
- One behavior per test. Name describes behavior: `test_<does_what>`.
- Use `pytest.raises` for expected exceptions, always with `match=` to verify the message.
- Use fixtures for setup, not setUp/tearDown. Scope fixtures correctly (function for DB, session for app).
- Use `@pytest.mark.parametrize` for edge cases instead of duplicating test functions.
- Don't mock the SUT. Mock external boundaries (HTTP, DB, email, filesystem).
- Use `factory_boy` or custom factories for test data, not raw inserts.
- Run with `pytest --durations=10` to find slow tests.
- Use `pytest -x` to stop on first failure during development.

---

## JavaScript/TypeScript — Jest / Vitest

### Structure
```javascript
// src/services/userService.test.ts
import { UserService } from './userService';
import { mockDb, mockEmailClient } from '../test/mocks';

describe('UserService', () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService(mockDb, mockEmailClient);
    mockDb.query.mockReset();
  });

  it('creates a user with valid data', async () => {
    mockDb.insert.mockResolvedValue({ id: 1 });
    const user = await service.create('test@example.com', 'Test');
    expect(user.id).toBe(1);
    expect(user.email).toBe('test@example.com');
  });

  it('rejects duplicate email', async () => {
    mockDb.query.mockResolvedValue([{ email: 'dup@example.com' }]);
    await expect(service.create('dup@example.com', 'Test'))
      .rejects.toThrow('already exists');
  });
});
```

### Fixtures and factories
```javascript
// test/factories/user.ts
export function createUser(overrides = {}) {
  return {
    id: Math.floor(Math.random() * 1000000),
    email: `user${Date.now()}@example.com`,
    name: 'Test User',
    ...overrides,
  };
}

// Usage
const user = createUser({ email: 'specific@example.com' });
```

### Parametrized
```javascript
it.each([
  ['user@example.com', true],
  ['invalid', false],
  ['', false],
  ['user@.com', false],
])('validates email "%s" as %s', (email, expected) => {
  expect(validateEmail(email)).toBe(expected);
});
```

### Mocking external boundaries
```javascript
import { jest } from '@jest/globals';

// Mock a module
jest.mock('./emailClient', () => ({
  send: jest.fn(),
}));

import { send } from './emailClient';

it('sends email on signup', async () => {
  send.mockResolvedValue(true);
  await service.create('test@example.com', 'Test');
  expect(send).toHaveBeenCalledTimes(1);
  expect(send).toHaveBeenCalledWith(expect.objectContaining({
    to: 'test@example.com',
  }));
});
```

### Async
```javascript
it('fetches user', async () => {
  const user = await fetchUser(1);
  expect(user.id).toBe(1);
});
```

### Best practices
- `describe` blocks group related tests. `it` describes behavior.
- Use `beforeEach` for per-test setup, `beforeAll` for expensive one-time setup.
- Use `jest.fn()` / `vi.fn()` for mocks. Reset in `beforeEach` with `mockReset()`.
- Use `expect(...).rejects.toThrow()` for async error assertions.
- Use `it.each` for parametrized tests.
- Don't mock the SUT. Mock external modules.
- Use factories for test data. Avoid hardcoded objects.
- Run with `--coverage` to get coverage. Don't chase numbers.
- Use `--verbose` to see test names.

---

## Go — testing

### Structure
```go
// user_service_test.go
package services

import (
    "testing"
    "errors"
)

func TestCreateUser_ValidData(t *testing.T) {
    svc := NewUserService(mockDB{})
    user, err := svc.Create("test@example.com", "Test")
    if err != nil {
        t.Fatalf("expected no error, got %v", err)
    }
    if user.ID == 0 {
        t.Error("expected non-zero ID")
    }
    if user.Email != "test@example.com" {
        t.Errorf("expected email test@example.com, got %s", user.Email)
    }
}

func TestCreateUser_DuplicateEmail(t *testing.T) {
    svc := NewUserService(mockDB{existing: []string{"dup@example.com"}})
    _, err := svc.Create("dup@example.com", "Test")
    if !errors.Is(err, ErrDuplicate) {
        t.Errorf("expected ErrDuplicate, got %v", err)
    }
}
```

### Table-driven tests
```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        email string
        valid bool
    }{
        {"user@example.com", true},
        {"invalid", false},
        {"", false},
        {"user@.com", false},
    }
    for _, tt := range tests {
        t.Run(tt.email, func(t *testing.T) {
            if got := ValidateEmail(tt.email); got != tt.valid {
                t.Errorf("ValidateEmail(%q) = %v, want %v", tt.email, got, tt.valid)
            }
        })
    }
}
```

### Mocking with interfaces
```go
type mockDB struct {
    existing []string
    inserted *User
}

func (m mockDB) Exists(email string) bool {
    for _, e := range m.existing {
        if e == email { return true }
    }
    return false
}

func (m *mockDB) Insert(u *User) error {
    m.inserted = u
    return nil
}
```

### Best practices
- Test files end with `_test.go` and are in the same package.
- Table-driven tests are the idiomatic pattern for edge cases.
- Use `t.Run` for subtests. Use `t.Fatalf` for fatal failures, `t.Errorf` for non-fatal.
- Mock by implementing interfaces. Use `testify/mock` or `gomock` for complex cases.
- Use `testify/assert` or `testify/require` for cleaner assertions (optional).
- Run with `go test -v ./...` for verbose output. `go test -cover` for coverage.
- Use `t.Cleanup()` for teardown.

---

## Rust — cargo test

### Structure
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn creates_user_with_valid_data() {
        let svc = UserService::new(mock_db());
        let user = svc.create("test@example.com", "Test").unwrap();
        assert_eq!(user.email, "test@example.com");
        assert!(user.id > 0);
    }

    #[test]
    fn rejects_duplicate_email() {
        let svc = UserService::new(mock_db_with("dup@example.com"));
        let result = svc.create("dup@example.com", "Test");
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), AppError::Duplicate));
    }
}
```

### Best practices
- Tests go in `#[cfg(test)] mod tests` at the bottom of the file, or in `tests/` for integration tests.
- Use `assert!`, `assert_eq!`, `assert_ne!` for assertions.
- Use `Result<T, E>` in tests to propagate errors: `fn test_foo() -> Result<(), Box<dyn Error>>`.
- Mock with `mockall` crate for external dependencies.
- Use `rstest` crate for parametrized tests.
- Run with `cargo test`. Use `cargo test -- --nocapture` to see println output.
- Use `cargo tarpaulin` or `cargo llvm-cov` for coverage.

---

## Ruby — RSpec

### Structure
```ruby
require 'rails_helper'

RSpec.describe UserService, type: :service do
  describe '#create' do
    it 'creates a user with valid data' do
      service = UserService.new
      user = service.create(email: 'test@example.com', name: 'Test')
      expect(user.id).not_to be_nil
      expect(user.email).to eq('test@example.com')
    end

    it 'rejects duplicate email' do
      create(:user, email: 'dup@example.com')
      service = UserService.new
      expect {
        service.create(email: 'dup@example.com', name: 'Second')
      }.to raise_error(ActiveRecord::RecordInvalid)
    end
  end
end
```

### Best practices
- Use `describe` for methods, `context` for conditions, `it` for behavior.
- Use FactoryBot for test data: `create(:user)`, `build(:user)`.
- Use `expect(...).to` syntax, not `should`.
- Use `let` and `subject` for lazy evaluation of test data.
- Mock with `allow`/`expect` (RSpec mocks). Mock external services, not the SUT.
- Run with `bundle exec rspec`. Use `--format documentation` for readable output.

---

## E2E — Playwright / Cypress

### Playwright (TypeScript)
```typescript
import { test, expect } from '@playwright/test';

test('user can sign up', async ({ page }) => {
  await page.goto('/signup');
  await page.fill('[name=email]', 'test@example.com');
  await page.fill('[name=password]', 'SecurePass123!');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('h1')).toHaveText('Welcome');
});
```

### Cypress
```javascript
describe('Signup', () => {
  it('allows a new user to sign up', () => {
    cy.visit('/signup');
    cy.get('[name=email]').type('test@example.com');
    cy.get('[name=password]').type('SecurePass123!');
    cy.get('button[type=submit]').click();
    cy.url().should('include', '/dashboard');
    cy.get('h1').should('contain', 'Welcome');
  });
});
```

### Best practices
- E2E tests are expensive. Use them for critical user flows only.
- Keep the number small: 5-20 E2E tests, not 200.
- Use page object models or custom commands to reduce duplication.
- Reset the database between E2E test runs.
- Use `test.describe` / `describe` to group related E2E tests.
- Don't use E2E tests for unit-testable logic — move those down to unit tests.

---

## General Patterns (all frameworks)

### Test structure: Arrange-Act-Assert
```
1. Arrange: set up the preconditions (fixtures, mocks, data)
2. Act: call the code under test
3. Assert: verify the outcome
```
Keep these three sections visually separate. One Act per test.

### Naming: behavior, not implementation
- GOOD: `test_rejects_signup_with_duplicate_email`
- GOOD: `returns_404_when_user_not_found`
- BAD: `test_user_service`
- BAD: `test_it_works`

### Edge cases to always consider
- Empty input (empty string, empty list, 0, null/None/nil)
- Single item (list of one, one record)
- Maximum (max int, max length, boundary values)
- Invalid input (wrong type, malformed, negative where positive expected)
- Concurrent access (two requests at the same time)
- Failure of dependencies (DB down, API timeout, file missing)
- Permission boundaries (unauthorized user, wrong role, expired token)

### Regression tests for known bugs
When git history or issue context reveals a past bug:
1. Write a test that reproduces the bug (fails before the fix).
2. Verify the fix makes it pass.
3. Keep the test — it prevents the bug from returning.
Name it: `test_does_not_<bug_description>` or `test_regression_<issue_number>`.

### Coverage as a signal, not a goal
- 100% coverage with trivial tests = false confidence.
- 70% coverage with meaningful tests targeting critical paths = good.
- Use coverage to find UNTESTED code, not to chase a percentage.
- Always check branch coverage, not just line coverage.