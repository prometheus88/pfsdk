#!/bin/bash
# Fix empty structs in generated Solidity files by adding a placeholder field

set -e

# Find all generated .sol files
find solidity/src/generated -name "*.sol" -type f | while read -r file; do
    # Create a temporary file
    temp_file="${file}.tmp"
    
    # Process the file to add placeholder fields to empty structs
    awk '
    /struct [A-Za-z_][A-Za-z0-9_]* \{/ {
        struct_line = $0
        getline next_line
        if (next_line ~ /^[[:space:]]*\}/) {
            # Found empty struct, add placeholder
            print struct_line
            print "\t\tbool _placeholder; // Added to avoid empty struct compilation error"
            print next_line
        } else {
            print struct_line
            print next_line
        }
        next
    }
    { print }
    ' "$file" > "$temp_file"
    
    # Move temp file back
    mv "$temp_file" "$file"
done

echo "✅ Fixed empty structs in generated Solidity files"