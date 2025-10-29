# Sports Search & Filter Feature

## Overview
Added real-time search and category filtering to the profile sports editing page, matching the functionality from signup step 3.

## Features Implemented

### 1. **Real-time Search (Debounced)**
- Search bar with 150ms debounce delay
- Instant filtering as you type
- Searches sport names and descriptions
- Shows all matching results when searching (no pagination)

### 2. **Dropdown Quick Selection**
- Shows top 8 matching sports in dropdown
- Appears after typing 2+ characters
- 200ms debounce delay
- Click to instantly add sport to selection
- Auto-clears search after selection

### 3. **Category Filters**
- 6 category buttons: All, Team, Racket, Fitness, Water, Combat
- One-click filtering by sport category
- Active category highlighted in blue
- Resets search when changing categories

### 4. **Smart Pagination**
- Initially loads 15 sports
- "Load More" button shows remaining count
- Loads 10 more sports each click
- Disabled during search (shows all results)

### 5. **Selected Sports Display**
- Shows selected sports at top with gradient styling
- Click X button to remove
- Updates hidden form inputs automatically

## UI Components

### Search Bar
```html
<input type="text" id="sportSearch" placeholder="Search sports..." />
```

### Category Filter Buttons
```html
<button class="category-filter" data-category="team">Team</button>
```

### Dropdown Results
```html
<div class="sport-search-results">
  <div class="sport-search-item">
    <span class="sport-search-icon">⚽</span>
    <span class="sport-search-name">Football</span>
    <span class="sport-search-category">team</span>
  </div>
</div>
```

## Technical Details

### Debouncing
- **Main search**: 150ms delay for real-time filtering
- **Dropdown**: 200ms delay for quick selection
- Prevents excessive re-renders while typing

### Data Flow
1. Load all sports from `/api/sports/search/?limit=100`
2. Store in `allSports` array
3. Filter based on: category, search query, not selected
4. Render with pagination or show all (during search)
5. Update hidden inputs for form submission

### State Management
```javascript
let allSports = [];           // All available sports
let selectedSports = new Set(); // Selected sport IDs
let currentCategory = 'all';   // Active category filter
let searchQuery = '';          // Current search text
let displayedSportsCount = 0;  // Number of sports shown
```

## Files Modified

1. **templates/users/profile_edit_sports.html**
   - Added search bar HTML
   - Added category filter buttons
   - Added dropdown results container
   - Added load more button
   - Updated CSS for dropdown styling
   - Complete JavaScript rewrite with search/filter logic

## Testing

### Test Search
1. Type "foot" → should show football, futsal, etc.
2. Clear search → should restore initial view

### Test Filters
1. Click "Team" → should show only team sports
2. Click "Racket" → should switch to racket sports
3. Click "All" → should show all sports

### Test Dropdown
1. Type "ba" → dropdown shows basketball, baseball, badminton
2. Click a sport → should add to selected and clear search

### Test Pagination
1. Scroll down → should see "Load More (X more)" button
2. Click "Load More" → should load 10 more sports
3. Start searching → "Load More" should disappear

## Integration Points

- Uses existing API endpoint: `/api/sports/search/`
- Uses existing Django form submission
- Maintains compatibility with current validation
- Pre-selects user's existing sports on page load

## Browser Compatibility

- Modern browsers (ES6+ required)
- Fetch API for AJAX requests
- CSS Grid and Flexbox for layout
- Smooth animations with CSS transitions

## Future Enhancements

- Add sport icons/images
- Add sport popularity indicators
- Add "recently selected" suggestions
- Add keyboard navigation for dropdown
- Add accessibility improvements (ARIA labels)
