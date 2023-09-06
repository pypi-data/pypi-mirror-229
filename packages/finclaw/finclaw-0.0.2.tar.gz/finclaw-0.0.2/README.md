# Finclaw

Finclaw is a dedicated tool designed to fetch and
update price data for various assets from multiple vendors.
It has been designed to provide uniform data interface across multiple vendors.

### Vendors supported

- Finnhub
- FMP
- TwelveData

### Example usage

```bash
finclaw grab --start 2023-08-13 --end 2023-09-04 --frequency 1 --include-information p --vendor fmp --market TO
```