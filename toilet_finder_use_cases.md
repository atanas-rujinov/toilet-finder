
# 📘 Use Case Documentation: Toilet Finder App

## 🎯 Primary Users

1. **Public User (App Visitor)**
   - People using the app to find nearby public toilets.
2. **Toilet Reporter**
   - Any user who contributes by adding or updating toilet information.
3. **Administrator**
   - Manages the backend, verifies data integrity, and moderates user-submitted content.

## 📌 Use Cases

### Use Case 1: Find Nearby Toilets

- **Actor**: Public User  
- **Goal**: Locate public toilets closest to current location  
- **Trigger**: User opens the app and enables location access  
- **Preconditions**: Location permission is granted  
- **Main Flow**:
  1. User opens app.
  2. App requests and receives geolocation.
  3. Nearby toilets are shown on a map and in a list.
- **Postconditions**: User views nearby toilet options.

### Use Case 2: View Toilet Details

- **Actor**: Public User  
- **Goal**: View detailed information about a selected toilet  
- **Main Flow**:
  1. User taps on a toilet pin or list item.
  2. App displays detailed info: name, amenities, cleanliness, hours, etc.
- **Alternative Flow**: If details are incomplete, user sees a prompt to contribute.

### Use Case 3: Add a New Toilet

- **Actor**: Toilet Reporter  
- **Goal**: Add a toilet not currently listed in the app  
- **Main Flow**:
  1. User taps "Add Toilet."
  2. Fills in form: location, name, facilities, etc.
  3. Submits entry.
- **Postconditions**: Entry is submitted and pending admin approval (if required).

### Use Case 4: Edit Existing Toilet Info

- **Actor**: Toilet Reporter  
- **Goal**: Improve accuracy of existing toilet data  
- **Main Flow**:
  1. User selects a toilet entry.
  2. Taps “Edit.”
  3. Updates relevant fields.
  4. Submits changes.
- **Postconditions**: Changes are saved or sent for admin review.

### Use Case 5: Rate or Review a Toilet

- **Actor**: Public User  
- **Goal**: Provide feedback on a toilet  
- **Main Flow**:
  1. User opens toilet detail view.
  2. Taps “Rate” or “Leave a Review.”
  3. Submits star rating and optional comment.
- **Postconditions**: Feedback is stored and displayed with the toilet listing.

### Use Case 6: Moderate Content

- **Actor**: Administrator  
- **Goal**: Ensure toilet entries are accurate and appropriate  
- **Main Flow**:
  1. Admin logs into backend or moderation interface.
  2. Reviews pending submissions and edits.
  3. Approves or rejects content.
- **Postconditions**: Approved entries become visible to users.
