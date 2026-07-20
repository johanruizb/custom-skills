# Language Documentation Conventions

Reference guide for the documentation format each language expects. Always defer to the project's existing style if it differs from these defaults.

## Python

**Format:** Docstrings (PEP 257). Three styles commonly used:

### Google style (most common, recommended default)
```python
def calculate_tax(amount: float, region: str, exempt: bool = False) -> dict:
    """Calculate sales tax for a given amount and region.

    Applies regional tax rules and exemption logic. Results include
    breakdown by tax type for accounting reconciliation.

    Args:
        amount: Pre-tax amount in USD. Must be positive.
        region: ISO 3166-2 region code (e.g., "US-CA").
        exempt: If True, returns zero tax but still validates the region.

    Returns:
        Dict with keys: total_tax, breakdown (dict of tax_type -> amount),
        effective_rate.

    Raises:
        ValueError: If amount is negative or region is unknown.
        TaxServiceUnavailable: If the regional tax API is unreachable.

    Note:
        Region codes are validated against the tax_service registry.
        Exempt transactions are still logged for audit compliance.
    """
```

### Sphinx (reST) style
```python
def calculate_tax(amount, region, exempt=False):
    """Calculate sales tax for a given amount and region.

    :param amount: Pre-tax amount in USD. Must be positive.
    :param region: ISO 3166-2 region code.
    :param exempt: If True, returns zero tax.
    :returns: Dict with total_tax, breakdown, effective_rate.
    :raises ValueError: If amount is negative or region unknown.
    """
```

### NumPy style
```python
def calculate_tax(amount, region, exempt=False):
    """
    Calculate sales tax for a given amount and region.

    Applies regional tax rules and exemption logic.

    Parameters
    ----------
    amount : float
        Pre-tax amount in USD. Must be positive.
    region : str
        ISO 3166-2 region code.
    exempt : bool, optional
        If True, returns zero tax (default False).

    Returns
    -------
    dict
        Keys: total_tax, breakdown, effective_rate.

    Raises
    ------
    ValueError
        If amount is negative or region is unknown.
    """
```

**Module-level docstrings:** Always include for non-trivial modules.
**Class docstrings:** Describe the class purpose, not the class name.
**`__init__` docstrings:** Only if initialization has non-obvious behavior. Prefer class docstring.
**Private methods:** Document if behavior is complex; skip if trivial.

## JavaScript

**Format:** JSDoc

```javascript
/**
 * Calculate sales tax for a given amount and region.
 *
 * Applies regional tax rules and exemption logic. Results include
 * breakdown by tax type for accounting reconciliation.
 *
 * @param {number} amount - Pre-tax amount in USD. Must be positive.
 * @param {string} region - ISO 3166-2 region code (e.g., "US-CA").
 * @param {boolean} [exempt=false] - If true, returns zero tax.
 * @returns {{totalTax: number, breakdown: Object, effectiveRate: number}}
 *   Tax calculation result.
 * @throws {Error} If amount is negative or region is unknown.
 * @since 1.2.0
 */
function calculateTax(amount, region, exempt = false) {
```

## TypeScript

**Format:** TSDoc (similar to JSDoc but with type annotations from TS)

```typescript
/**
 * Calculate sales tax for a given amount and region.
 *
 * Applies regional tax rules and exemption logic.
 *
 * @param amount - Pre-tax amount in USD. Must be positive.
 * @param region - ISO 3166-2 region code.
 * @param exempt - If true, returns zero tax. Default: false.
 * @returns Tax calculation result with breakdown.
 * @throws {Error} If amount is negative or region is unknown.
 */
function calculateTax(amount: number, region: string, exempt = false): TaxResult {
```

Note: In TypeScript, types are already in the signature — don't duplicate them in @param tags. Describe semantics, not types.

## PHP

**Format:** PHPDoc

```php
/**
 * Calculate sales tax for a given amount and region.
 *
 * Applies regional tax rules and exemption logic.
 *
 * @param float  $amount  Pre-tax amount in USD. Must be positive.
 * @param string $region  ISO 3166-2 region code.
 * @param bool   $exempt  If true, returns zero tax.
 * @return array{total_tax: float, breakdown: array, effective_rate: float}
 * @throws \InvalidArgumentException If amount is negative or region unknown.
 */
public function calculateTax(float $amount, string $region, bool $exempt = false): array {
```

## Rust

**Format:** Rustdoc (triple-slash `///` or block `/** */`)

```rust
/// Calculate sales tax for a given amount and region.
///
/// Applies regional tax rules and exemption logic. Results include
/// breakdown by tax type for accounting reconciliation.
///
/// # Arguments
/// * `amount` - Pre-tax amount in USD. Must be positive.
/// * `region` - ISO 3166-2 region code.
/// * `exempt` - If true, returns zero tax.
///
/// # Returns
/// A `TaxResult` with total tax, breakdown, and effective rate.
///
/// # Errors
/// Returns `TaxError::InvalidAmount` if amount is negative.
/// Returns `TaxError::UnknownRegion` if region code is not found.
///
/// # Examples
/// ```
/// let result = calculate_tax(100.0, "US-CA", false)?;
/// assert_eq!(result.total_tax, 7.25);
/// ```
fn calculate_tax(amount: f64, region: &str, exempt: bool) -> Result<TaxResult, TaxError> {
```

## Java

**Format:** Javadoc

```java
/**
 * Calculate sales tax for a given amount and region.
 * <p>
 * Applies regional tax rules and exemption logic.
 *
 * @param amount Pre-tax amount in USD. Must be positive.
 * @param region ISO 3166-2 region code.
 * @param exempt If true, returns zero tax.
 * @return TaxResult with total tax, breakdown, and effective rate.
 * @throws IllegalArgumentException If amount is negative or region unknown.
 * @since 1.2.0
 */
public TaxResult calculateTax(double amount, String region, boolean exempt) {
```

## Go

**Format:** Doc comments (regular comments preceding declarations, no special syntax)

```go
// CalculateTax calculates sales tax for a given amount and region.
//
// Applies regional tax rules and exemption logic. Returns a TaxResult
// with breakdown by tax type. Returns an error if amount is negative
// or the region is unknown.
//
// Note: Exempt transactions are still logged for audit compliance.
func CalculateTax(amount float64, region string, exempt bool) (*TaxResult, error) {
```

Go convention: the comment starts with the function name. Keep it concise. Use `godoc` conventions — no markdown, plain text only.

## Ruby

**Format:** RDoc / YARD

```ruby
# Calculate sales tax for a given amount and region.
#
# Applies regional tax rules and exemption logic.
#
# @param amount [Float] Pre-tax amount in USD. Must be positive.
# @param region [String] ISO 3166-2 region code.
# @param exempt [Boolean] If true, returns zero tax.
# @return [Hash] Tax result with :total_tax, :breakdown, :effective_rate.
# @raise [ArgumentError] If amount is negative or region unknown.
def calculate_tax(amount, region, exempt: false)
```

## C#

**Format:** XML documentation comments

```csharp
/// <summary>
/// Calculate sales tax for a given amount and region.
/// </summary>
/// <remarks>
/// Applies regional tax rules and exemption logic.
/// </remarks>
/// <param name="amount">Pre-tax amount in USD. Must be positive.</param>
/// <param name="region">ISO 3166-2 region code.</param>
/// <param name="exempt">If true, returns zero tax.</param>
/// <returns>TaxResult with total tax, breakdown, and effective rate.</returns>
/// <exception cref="ArgumentException">
/// Thrown when amount is negative or region is unknown.
/// </exception>
public TaxResult CalculateTax(double amount, string region, bool exempt = false) {
```

## Swift

**Format:** Swift Markup (reStructuredText-style)

```swift
/// Calculate sales tax for a given amount and region.
///
/// Applies regional tax rules and exemption logic.
///
/// - Parameters:
///   - amount: Pre-tax amount in USD. Must be positive.
///   - region: ISO 3166-2 region code.
///   - exempt: If true, returns zero tax. Default: false.
/// - Returns: TaxResult with total tax, breakdown, and effective rate.
/// - Throws: ``TaxError`` if amount is negative or region is unknown.
func calculateTax(amount: Double, region: String, exempt: Bool = false) throws -> TaxResult {
```

## Kotlin

**Format:** KDoc (similar to JavaDoc but with Markdown support)

```kotlin
/**
 * Calculate sales tax for a given amount and region.
 *
 * Applies regional tax rules and exemption logic.
 *
 * @param amount Pre-tax amount in USD. Must be positive.
 * @param region ISO 3166-2 region code.
 * @param exempt If true, returns zero tax. Default: false.
 * @return [TaxResult] with total tax, breakdown, and effective rate.
 * @throws [IllegalArgumentException] If amount is negative or region unknown.
 */
fun calculateTax(amount: Double, region: String, exempt: Boolean = false): TaxResult {
```

## General rules across all languages

1. **Match existing project style.** If the project uses Google-style Python, don't switch to Sphinx.
2. **Types in signature → don't duplicate in docs.** For TS, Rust, Go with explicit types, describe semantics, not types.
3. **First line is a summary.** One sentence, imperative mood for Python/Rust, declarative for others.
4. **Blank line after summary.** Then details.
5. **Document the why, not the what.** Code shows what; docs explain why and what to watch out for.
6. **`@since` / version tags:** Only if the project already uses them.
7. **Examples:** Include only when they add real value (non-obvious usage, edge case handling).