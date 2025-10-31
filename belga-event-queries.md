# Belga Event Query Guide

## Overview
This guide documents the Production API queries for filtering events according to Belga's requirements:

- Calendar selection
- Region filtering (Belgium/International)
- Date range filtering 
- Text search
- Coverage type filtering

## Authentication
All requests require JWT authentication:

```bash
export PRODAPI="http://localhost:5500/prodapi/v1"
export JWT_TOKEN="your.jwt.token"
```

## Event Queries

### 1. Filter by Calendar
```json
GET /prodapi/v1/events
{
  "query": {
    "bool": {
      "filter": [
        { "terms": { "calendars._id": ["CALENDAR_ID_1", "CALENDAR_ID_2"] } }
      ]
    }
  }
}
```

### 2. Filter by Region
For Belgian events:
```json
GET /prodapi/v1/events
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "location.address.country": "Belgium" } }
      ]
    }
  }
}
```

For International events:
```json
GET /prodapi/v1/events
{
  "query": {
    "bool": {
      "must_not": [
        { "term": { "location.address.country": "Belgium" } }
      ]
    }
  }
}
```

### 3. Filter by Date Range
```json
GET /prodapi/v1/events
{
  "query": {
    "bool": {
      "filter": [
        {
          "range": {
            "dates.start": {
              "gte": "2025-10-01T00:00:00Z",
              "lte": "2025-10-31T23:59:59Z"
            }
          }
        }
      ]
    }
  }
}
```

### 4. Text Search
```json
GET /prodapi/v1/events
{
  "query": {
    "multi_match": {
      "query": "search text",
      "fields": ["name^3", "definition", "slugline", "description"]
    }
  }
}
```

### 5. Filter by Coverage Type
This requires a two-step process:

1. First, query planning items with specific coverage type:
```json
GET /prodapi/v1/planning
{
  "query": {
    "nested": {
      "path": "coverages",
      "query": {
        "bool": {
          "filter": [
            { "term": { "coverages.g2_content_type": "text" } }
          ]
        }
      }
    }
  }
}
```

2. Then query events using event IDs from planning response:
```json
GET /prodapi/v1/events
{
  "query": {
    "terms": {
      "_id": ["EVENT_ID_1", "EVENT_ID_2"]
    }
  }
}
```

## Combined Query Example
```json
GET /prodapi/v1/events
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "search text",
            "fields": ["name", "definition"]
          }
        }
      ],
      "filter": [
        { "terms": { "calendars._id": ["CALENDAR_ID"] } },
        { "term": { "location.address.country": "Belgium" } },
        {
          "range": {
            "dates.start": {
              "gte": "2025-10-01T00:00:00Z",
              "lte": "2025-10-31T23:59:59Z"
            }
          }
        }
      ]
    }
  }
}
```

## Usage Examples

### Curl Examples
```bash
# Filter by calendar
curl -g -H "Authorization: Bearer $JWT_TOKEN" \
  "$PRODAPI/events?source={\"query\":{\"bool\":{\"filter\":[{\"terms\":{\"calendars._id\":[\"CALENDAR_ID\"]}}]}}}"

# Filter by region (Belgium)
curl -g -H "Authorization: Bearer $JWT_TOKEN" \
  "$PRODAPI/events?source={\"query\":{\"bool\":{\"filter\":[{\"term\":{\"location.address.country\":\"Belgium\"}}]}}}"

# Filter by date range
curl -g -H "Authorization: Bearer $JWT_TOKEN" \
  "$PRODAPI/events?source={\"query\":{\"bool\":{\"filter\":[{\"range\":{\"dates.start\":{\"gte\":\"2025-10-01T00:00:00Z\",\"lte\":\"2025-10-31T23:59:59Z\"}}}]}}}"
```

## Notes
- All queries support pagination using `size` and `from` parameters
- Sort results using the `sort` parameter
- Response format follows HATEOAS with linked resources
- Coverage type filtering requires two API calls
- All date fields should be in ISO 8601 format with timezone
