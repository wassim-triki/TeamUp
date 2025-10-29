# Sports Pre-selection Flow

## How User's Already-Selected Sports Are Loaded

### 1. Backend (views.py)
```python
@login_required
def edit_sports(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user's current sports as list of IDs
    user_sports = list(profile.interested_sports.values_list('id', flat=True))
    # Example: [1, 5, 12, 23] if user has selected 4 sports
    
    context = {
        'user_sports': user_sports,  # Passed to template
        ...
    }
    return render(request, 'users/profile_edit_sports.html', context)
```

### 2. Template Rendering
The Django template engine converts Python list to JavaScript array:
```html
<script>
    const userSports = {{ user_sports|safe }};
    // Renders as: const userSports = [1, 5, 12, 23];
</script>
```

### 3. JavaScript Loading Sequence
```javascript
async function loadSports() {
    // Step 1: Fetch all available sports from API
    const response = await fetch('/api/sports/search/?limit=100');
    const data = await response.json();
    allSports = data.results;  // Store all 100 sports
    
    // Step 2: Pre-select user's current sports
    const userSports = [1, 5, 12, 23];  // From Django template
    userSports.forEach(sportId => {
        const sport = allSports.find(s => s.id === sportId);
        if (sport) {
            selectedSports.add(sport.id);  // Add to Set
        }
    });
    
    // Step 3: Render selected sports at TOP (blue gradient)
    renderSelectedSports();
    
    // Step 4: Render available sports BELOW (white background)
    // These exclude already selected sports
    renderAvailableSports(INITIAL_LOAD);
    
    // Step 5: Update hidden form inputs
    updateHiddenInputs();
}
```

### 4. Visual Result

**Selected Sports Section (Top):**
```
┌─────────────────────────────────────────┐
│ Selected Sports (Blue Gradient)         │
├─────────────────────────────────────────┤
│ ⚽ Football [×]  ��� Basketball [×]      │
│ ��� Tennis [×]   ⛳ Golf [×]            │
└─────────────────────────────────────────┘
```

**Available Sports Section (Below):**
```
┌─────────────────────────────────────────┐
│ Available Sports (White Background)     │
├─────────────────────────────────────────┤
│ ��� Swimming    ��� Volleyball           │
│ ��� Table Tennis  ��� Boxing            │
│ ... (first 15 sports, excluding selected)│
└─────────────────────────────────────────┘
```

## Data Flow Diagram

```
Database (MySQL)
    ↓
UserProfile.interested_sports (M2M relationship)
    ↓
Django View: user_sports = [1, 5, 12, 23]
    ↓
Template Context: {{ user_sports|safe }}
    ↓
JavaScript: const userSports = [1, 5, 12, 23];
    ↓
selectedSports Set: {1, 5, 12, 23}
    ↓
renderSelectedSports() → Shows blue capsules with X button
    ↓
renderAvailableSports() → Shows white capsules (excluding IDs 1,5,12,23)
    ↓
Form Submission → Hidden inputs with selected IDs
```

## Key Functions

### renderSelectedSports()
```javascript
function renderSelectedSports() {
    const container = document.getElementById('selectedSportsContainer');
    const selectedSportsList = Array.from(selectedSports)
        .map(id => allSports.find(s => s.id === id))
        .filter(Boolean);
    
    container.innerHTML = selectedSportsList.map(sport => `
        <div class="sport-capsule">
            <label style="background: linear-gradient(135deg, #50b5ff 0%, #2e8bc0 100%);">
                <span>${sport.emoji}</span>
                <span>${sport.name}</span>
                <button onclick="deselectSport(${sport.id})">×</button>
            </label>
        </div>
    `).join('');
}
```

### getFilteredSports()
```javascript
function getFilteredSports() {
    return allSports.filter(sport => {
        const notSelected = !selectedSports.has(sport.id);  // Exclude selected
        const matchesCategory = currentCategory === 'all' || sport.category === currentCategory;
        const matchesSearch = !searchQuery || sport.name.toLowerCase().includes(searchQuery);
        
        return notSelected && matchesCategory && matchesSearch;
    });
}
```

## Example Scenario

**User Profile has 3 sports:**
- Football (id: 1)
- Basketball (id: 5)
- Tennis (id: 12)

**Page Load Sequence:**
1. ✅ Fetch 100 sports from API
2. ✅ Add IDs [1, 5, 12] to selectedSports Set
3. ✅ Render 3 blue gradient capsules at top
4. ✅ Render 15 white capsules below (excluding IDs 1, 5, 12)
5. ✅ Create 3 hidden inputs: `<input name="sports" value="1">`

**User Adds Golf (id: 23):**
1. Click Golf capsule
2. selectedSports becomes {1, 5, 12, 23}
3. Re-render: 4 blue capsules at top
4. Re-render: Available sports (excluding 1, 5, 12, 23)
5. Update hidden inputs: 4 inputs now

**User Removes Tennis:**
1. Click X on Tennis capsule
2. selectedSports becomes {1, 5, 23}
3. Re-render: 3 blue capsules (Football, Basketball, Golf)
4. Re-render: Available sports now includes Tennis again
5. Update hidden inputs: 3 inputs now

## Form Submission

When user clicks "Save Changes":
```html
<form method="POST">
    <input type="hidden" name="sports" value="1">
    <input type="hidden" name="sports" value="5">
    <input type="hidden" name="sports" value="23">
    <button type="submit">Save Changes</button>
</form>
```

Django receives: `['1', '5', '23']`
Updates database: `profile.interested_sports.set([1, 5, 23])`

## Testing Checklist

✅ **Page Load**
- User's existing sports appear as blue capsules at top
- Available sports section excludes user's sports
- Hidden inputs match selected sports

✅ **Add Sport**
- Click white capsule → becomes blue and moves to top
- Sport disappears from available section
- Hidden input added

✅ **Remove Sport**
- Click X on blue capsule → disappears
- Sport reappears in available section (white)
- Hidden input removed

✅ **Search While Pre-selected**
- Type "foot" → filters available sports
- Selected sports remain at top (not filtered)

✅ **Category Filter While Pre-selected**
- Click "Team" → filters available sports by category
- Selected sports remain at top (all categories shown)

✅ **Form Submission**
- Selected sports saved to database
- Page reload shows same sports as selected
