# Data Structure


JSON file structure for storing data:

```json
[
    {
        "id": "string",         // Unique profile identifier (our internal ID)
        "name": "string",       // Profile name
        "age": integer,         // Profile age
        "lives_in": "string",  // Location or city
        // "image_paths": ["string", "string", ...],  // List of local paths to downloaded images
        "about_me": "string",    // Text from the 'About Me' section (Optional)
        "essentials": ["string", "string", ...], // List of essentials (Optional)
        "lifestyle": ["string", "string", ...],    // List of lifestyle attributes (Optional)
        "interests": ["string", "string", ...],  // List of interests (Optional)
    },
    ...
]
```