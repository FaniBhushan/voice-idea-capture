-- AppleScript: Export Apple Notes tagged with #idea
-- This script queries macOS Notes, writes the raw contents of #idea notes to files in the input folder,
-- and moves the processed notes to a "Processed Ideas" folder in Apple Notes to prevent duplicates.

-- CONFIGURATION
-- Update this to point to your actual project input directory path
set projectInputPath to "/Users/fanibhushan/voice-idea-capture/input/"

-- Helper function to write text to a file
on writeTextToFile(textData, filePath)
    try
        set fileReference to open for access POSIX file filePath with write permission
        set eof of fileReference to 0 -- Clear existing content if any
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

tell application "Notes"
    -- Check if "Processed Ideas" folder exists, create it if not
    if not (exists folder "Processed Ideas") then
        make new folder with properties {name:"Processed Ideas"}
    end if
    
    set ideaNotes to {}
    
    -- Gather all notes that contain the #idea tag
    -- AppleScript filter for body text search
    set allNotes to every note
    repeat with aNote in allNotes
        if (body of aNote contains "#idea") or (plaintext of aNote contains "#idea") then
            copy aNote to end of ideaNotes
        end if
    end repeat
    
    set exportCount to 0
    
    repeat with theNote in ideaNotes
        set noteName to name of theNote
        set noteBody to plaintext of theNote
        set noteId to id of theNote
        
        -- Generate safe filename
        set safeName to my sanitizeFilename(noteName)
        if safeName is "" then
            set safeName to "Note_" & (current date's time string)
        end if
        
        -- Assemble full destination path
        set exportFilename to safeName & "_" & (current date's time as integer) & ".txt"
        set exportFilePath to projectInputPath & exportFilename
        
        -- Export content
        set success to my writeTextToFile(noteBody, exportFilePath)
        
        if success then
            -- Move note to the "Processed Ideas" folder in Apple Notes to prevent reprocessing
            move theNote to folder "Processed Ideas"
            set exportCount to exportCount + 1
        end if
    end repeat
    
    if exportCount > 0 then
        display notification "Successfully exported " & exportCount & " notes to the Ingestion pipeline." with title "Idea Exporter"
    end if
end tell
