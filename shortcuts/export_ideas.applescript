-- AppleScript: Export Apple Notes tagged with @idea
-- This script queries macOS Notes, writes the raw contents of @idea notes to files in the input folder,
-- and moves the processed notes to a "Processed Ideas" folder in Apple Notes to prevent duplicates.
-- Returns the count of exported notes.

-- CONFIGURATION
property projectInputPath : "/Users/fanibhushan/.voice-idea-capture/input/"

tell application "Notes"
    -- Check if "Processed Ideas" folder exists, create it if not
    if not (exists folder "Processed Ideas") then
        make new folder with properties {name:"Processed Ideas"}
    end if
    
    set ideaNotes to {}
    
    -- Gather all notes that contain the @idea tag and are not in "Processed Ideas" or "Recently Deleted"
    set allNotes to every note
    repeat with aNote in allNotes
        set noteFolder to container of aNote
        set folderName to name of noteFolder
        if (folderName is not "Processed Ideas") and (folderName is not "Recently Deleted") then
            if (body of aNote contains "@idea") or (plaintext of aNote contains "@idea") then
                copy aNote to end of ideaNotes
            end if
        end if
    end repeat
    
    set exportCount to 0
    
    repeat with theNote in ideaNotes
        set noteName to name of theNote
        set noteBody to plaintext of theNote
        
        -- Generate safe filename
        set safeName to my sanitizeFilename(noteName)
        if safeName is "" then
            set safeName to "Note_" & (time of (current date))
        end if
        
        -- Assemble full destination path
        set exportFilename to safeName & "_" & (time of (current date)) & ".txt"
        set exportFilePath to projectInputPath & exportFilename
        
        -- Export content
        set success to my writeTextToFile(noteBody, exportFilePath)
        
        if success then
            -- Move note to the "Processed Ideas" folder in Apple Notes
            move theNote to folder "Processed Ideas"
            set exportCount to exportCount + 1
        end if
    end repeat
    
    return exportCount
end tell

-- Helper function to write text to a file
on writeTextToFile(textData, filePath)
    try
        set fileReference to open for access POSIX file filePath with write permission
        set eof of fileReference to 0
        write textData to fileReference starting at eof as «class utf8»
        close access fileReference
        return true
    on error msg
        try
            close access file filePath
        end try
        log "Error writing to file: " & msg
        return false
    end try
end writeTextToFile

-- Helper function to replace characters for safe filenames
on sanitizeFilename(rawName)
    set cleanName to ""
    set allowedChars to "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ "
    repeat with char in rawName
        if char is in allowedChars then
            set cleanName to cleanName & char
        else
            set cleanName to cleanName & "_"
        end if
    end repeat
    if length of cleanName > 50 then
        set cleanName to text 1 thru 50 of cleanName
    end if
    return cleanName
end sanitizeFilename
