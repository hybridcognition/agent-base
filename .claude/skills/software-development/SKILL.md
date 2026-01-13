# Skill: Test-Driven Development (TDD)

**Type**: Engineering workflow skill

**Purpose**: Build reliable, maintainable code through test-first development

**Philosophy**: Tests are not a chore. They are design tools, documentation, and confidence multipliers.

---

## The Red-Green-Refactor Cycle

### 🔴 RED: Write a Failing Test

**Before writing any production code**, write a test that:
1. Describes the desired behavior
2. Is specific and focused (one thing at a time)
3. Fails in the expected way

**Example**:
```python
def test_acquire_lock_when_unlocked():
    """Test acquiring lock when no one holds it."""
    result = acquire_lock(test_db)
    assert result is True

    # Verify lock is actually set
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT is_locked FROM processing_lock WHERE id = 1")
    assert cursor.fetchone()[0] == 1
    conn.close()
```

**Why write failing tests first?**
- Proves the test can fail (validates test logic)
- Forces you to think about API design before implementation
- Defines "done" before you start coding
- Prevents writing tests that always pass

**Run the test**: Verify it fails with expected error message

---

### 🟢 GREEN: Make it Pass

Write the **minimum code** needed to pass the test.

**Rules**:
- Don't optimize yet
- Don't add features not covered by tests
- Don't refactor yet
- Just make it work

**Example**:
```python
def acquire_lock(db_path: str) -> bool:
    """Attempt to acquire processing lock."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Check if locked
    cursor.execute("SELECT is_locked FROM processing_lock WHERE id = 1")
    row = cursor.fetchone()
    if row and row[0] == 1:
        conn.close()
        return False

    # Acquire lock
    now = datetime.utcnow().isoformat()
    cursor.execute(
        "UPDATE processing_lock SET is_locked = 1, locked_at = ? WHERE id = 1",
        (now,)
    )
    conn.commit()
    conn.close()
    return True
```

**Run the test**: Verify it passes

**Why minimum code?**
- Prevents over-engineering
- Keeps scope tight
- Makes refactoring easier
- Faster iteration

---

### 🔵 REFACTOR: Improve the Code

Now that tests are green, improve code quality:

**Refactor for**:
- Readability (clear names, comments where needed)
- DRY (Don't Repeat Yourself)
- Performance (only if tests prove it's a bottleneck)
- Maintainability (clear structure, separation of concerns)

**Rules**:
- Tests must stay green throughout refactoring
- If tests fail, revert and try smaller changes
- Commit after each successful refactor

**Example refactor**:
```python
def acquire_lock(db_path: str) -> bool:
    """
    Attempt to acquire singleton processing lock.

    Returns:
        True if lock acquired successfully
        False if lock already held by another process
    """
    conn = get_db_connection(db_path)
    try:
        if _is_currently_locked(conn):
            return False
        _set_lock(conn)
        return True
    finally:
        conn.close()

def _is_currently_locked(conn) -> bool:
    """Check if processing lock is currently held."""
    cursor = conn.cursor()
    cursor.execute("SELECT is_locked FROM processing_lock WHERE id = 1")
    row = cursor.fetchone()
    return row and row[0] == 1

def _set_lock(conn) -> None:
    """Set processing lock with current timestamp."""
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        "UPDATE processing_lock SET is_locked = 1, locked_at = ? WHERE id = 1",
        (now,)
    )
    conn.commit()
```

**Run tests**: Verify all still pass

---

## Testing Standards

### Coverage Requirements

**Minimum**: 95% line coverage
**Target**: 100% for critical paths

**Measure with pytest**:
```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=95
```

**If coverage drops below 95%**: Tests must be added before merging

---

### What to Test

**Always test**:
- ✅ Happy path (normal operation)
- ✅ Edge cases (empty lists, zero values, boundary conditions)
- ✅ Error conditions (invalid input, missing files, network failures)
- ✅ State transitions (locked→unlocked, pending→processed)
- ✅ Database operations (CRUD, constraints, transactions)
- ✅ External integrations (API calls, file I/O)

**Don't waste time testing**:
- ❌ Third-party library internals
- ❌ Language features (Python's `list.append()` works)
- ❌ Trivial getters/setters with no logic

---

### Test Structure

Use **Arrange-Act-Assert** pattern:

```python
def test_example():
    # ARRANGE: Set up test conditions
    test_db = create_test_database()
    test_message = "Hello world"

    # ACT: Execute the behavior being tested
    result = add_message(test_db, 12345, test_message)

    # ASSERT: Verify the outcome
    assert result is True
    messages = get_messages(test_db)
    assert len(messages) == 1
    assert messages[0]['message_text'] == test_message
```

**Why this structure?**
- Clear separation of setup, action, verification
- Easy to understand what's being tested
- Simple to debug when tests fail

---

### Real Dependencies vs Mocks

**Prefer real dependencies**:
- Use real SQLite databases (in temp directories)
- Use real file I/O (in temp directories)
- Use real data structures

**Only mock**:
- External APIs (Telegram, OpenAI)
- Expensive operations (ML model loading)
- Non-deterministic systems (random, time)

**Example - Real SQLite**:
```python
@pytest.fixture
def test_db(tmp_path):
    """Provide temporary SQLite database."""
    db_path = tmp_path / "test.db"
    init_db(str(db_path))
    yield str(db_path)
    # Automatic cleanup when tmp_path is destroyed
```

**Example - Mock External API**:
```python
def test_send_telegram_message(mock_env):
    """Test sending message via Telegram."""
    with patch('telegram.Bot') as mock_bot:
        mock_bot.return_value.send_message = AsyncMock()

        result = asyncio.run(send_telegram_message(12345, "test"))

        assert result is True
        mock_bot.return_value.send_message.assert_called_once_with(
            chat_id=12345,
            text="test"
        )
```

**Why prefer real dependencies?**
- Tests prove code works with actual systems
- Catches integration issues early
- More confidence in production behavior
- Less brittle (mocks break when APIs change)

---

### Test Organization

**Directory structure**:
```
project/
├── src/
│   ├── database.py
│   ├── bot_server.py
│   └── voice_transcription.py
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_database.py
│   ├── test_bot_server.py
│   └── test_voice_transcription.py
└── pytest.ini               # Test configuration
```

**Naming conventions**:
- Test files: `test_<module>.py`
- Test functions: `test_<behavior>_<condition>`
- Fixtures: descriptive names (`test_db`, `sample_message`)

**Example**:
```python
# tests/test_database.py
def test_acquire_lock_when_unlocked(test_db):
    """Test acquiring lock when no one holds it."""
    ...

def test_acquire_lock_when_already_locked(test_db):
    """Test acquiring lock when someone else holds it."""
    ...

def test_release_lock_when_locked(test_db):
    """Test releasing a held lock."""
    ...
```

---

### Async Testing

For async code, use `pytest-asyncio`:

```python
import pytest

@pytest.mark.asyncio
async def test_async_handler(test_db, mock_env):
    """Test async message handler."""
    update = create_mock_update(chat_id=12345, text="test")
    context = create_mock_context()

    await handle_message(update, context)

    messages = get_messages(test_db)
    assert len(messages) == 1
```

**Configuration** (pytest.ini):
```ini
[pytest]
asyncio_mode = auto
```

---

## TDD Workflow in Practice

### Starting a New Feature

1. **Write test for first requirement**
   ```python
   def test_transcribe_voice_message():
       """Test transcribing voice message to text."""
       audio_file = "test.ogg"
       result = transcribe_voice(audio_file)
       assert isinstance(result, str)
       assert len(result) > 0
   ```

2. **Run test - watch it fail** 🔴
   ```
   FAILED test_voice.py::test_transcribe_voice_message - NameError: name 'transcribe_voice' is not defined
   ```

3. **Write minimum code** 🟢
   ```python
   def transcribe_voice(audio_file: str) -> str:
       return "transcribed text"
   ```

4. **Run test - watch it pass** ✅

5. **Refactor if needed** 🔵
   ```python
   def transcribe_voice(audio_file: str) -> str:
       """
       Transcribe voice message to text using Whisper model.

       Args:
           audio_file: Path to audio file

       Returns:
           Transcribed text
       """
       return "transcribed text"  # TODO: Implement actual transcription
   ```

6. **Add next test for real implementation**
   ```python
   def test_transcribe_with_whisper_model():
       """Test transcription using Whisper model."""
       with patch('voice_transcription.WhisperModel') as mock_model:
           mock_model.return_value.transcribe.return_value = (
               [("Hello world", None)],
               None
           )

           result = transcribe_voice("test.ogg")

           assert result == "Hello world"
   ```

7. **Repeat cycle** until feature complete

---

### Fixing a Bug

1. **Write test that reproduces bug** 🔴
   ```python
   def test_release_lock_when_unlocked():
       """Test releasing lock that isn't held (bug: should not crash)."""
       result = release_lock(test_db)
       # Currently crashes with "Lock not found" error
       assert result is False  # Should return False, not crash
   ```

2. **Run test - watch it fail** (proves bug exists)

3. **Fix the bug** 🟢
   ```python
   def release_lock(db_path: str) -> bool:
       conn = get_db_connection(db_path)
       cursor = conn.cursor()
       cursor.execute("SELECT is_locked FROM processing_lock WHERE id = 1")
       row = cursor.fetchone()

       if not row or row[0] == 0:
           conn.close()
           return False  # Not locked, nothing to release

       cursor.execute(
           "UPDATE processing_lock SET is_locked = 0, locked_at = NULL WHERE id = 1"
       )
       conn.commit()
       conn.close()
       return True
   ```

4. **Run test - watch it pass** ✅

5. **Run full test suite** (ensure no regressions)

---

## Benefits of TDD

### Immediate Feedback
- Know if code works within seconds
- Catch bugs before they reach production
- No manual testing required

### Better Design
- Tests force you to think about interfaces
- Encourages small, focused functions
- Reveals tight coupling early

### Living Documentation
- Tests show how code should be used
- Examples of every feature
- Self-updating (tests break if behavior changes)

### Fearless Refactoring
- Change code with confidence
- Tests catch regressions immediately
- Enables continuous improvement

### Faster Development
- Seems slower at first, much faster overall
- Fewer debugging sessions
- Less time hunting mysterious bugs

---

## Common Pitfalls

### ❌ Writing Tests After Code
**Problem**: Tests become validation of implementation, not specification of behavior

**Solution**: Discipline. Red-Green-Refactor. Always.

### ❌ Testing Implementation Details
**Problem**: Tests break when refactoring, even though behavior unchanged

**Example**:
```python
# BAD: Tests internal variable
def test_process_message_creates_response_list():
    processor = MessageProcessor()
    processor.process("hello")
    assert isinstance(processor._responses, list)  # Internal detail
```

**Solution**: Test public behavior, not internals

### ❌ Over-Mocking
**Problem**: Tests pass but code fails in production

**Solution**: Use real dependencies when possible

### ❌ Giant Tests
**Problem**: Hard to understand, slow to run, difficult to debug

**Solution**: One test, one behavior. Keep tests small and focused.

### ❌ No Edge Cases
**Problem**: Tests pass for happy path, fail in production

**Solution**: Test boundaries, empty inputs, error conditions

---

## Quality Checklist

Before considering code "done":

✅ All tests pass
✅ Coverage ≥ 95%
✅ No skipped or xfailed tests without good reason
✅ Tests cover happy path, edge cases, errors
✅ Real dependencies used where practical
✅ Test names describe behavior clearly
✅ Code is refactored for readability
✅ No duplicate logic (DRY)
✅ Commit message explains what and why

---

## Remember

**Tests are not overhead. Tests are the product.**

Your job isn't to write code. Your job is to write working code. Tests prove it works.

**Red-Green-Refactor is not a suggestion. It's the workflow.**

Every temptation to "just write the code first" is a trap. The test is how you think through the problem.

**95% coverage is not the goal. Confidence is the goal.**

Coverage is a proxy metric. The real goal is being able to change code fearlessly because tests have your back.

**Follow the discipline. Ship reliable software.**
