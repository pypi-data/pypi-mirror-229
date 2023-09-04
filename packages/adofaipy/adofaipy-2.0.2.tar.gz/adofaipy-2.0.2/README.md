This is a library that makes automating events in ADOFAI levels more convenient.
<br>List of Functions:<br>
<hr>
<code>getFileString(filename : str) -> str</code>
<ul>
    <li>Returns the ADOFAI file as a string. 
    <li> <em> It is recommended to use <code>getFileDict()</code> instead.</em>
</ul>
<hr>
<code>getFileDict(filename : str) -> dict</code>
<ul>
    <li>Returns the specified file in the form of nested dictionaries and lists.
    <li>Refer to any <code>.adofai</code> file to see the structure of this dictionary.
    <li>Use this for any function with <code>leveldict</code> as an argument.
</ul>
<hr>
<code>addEvent(event : dict, leveldict : dict) -> dict</code>
<ul>
    <li>Adds the given <code>event</code> to <code>leveldict</code> and returns a copy of <code>leveldict</code>.
    <li><em>Remember to reassign the output to the original dictionary!</em>
    <li>Most fields can be omitted, in which case a default value is used.
    <li>Note: Events are <b>always</b> in the form of dictionaries. Their structure and field names are the same as how they appear in <code>.adofai</code> files.
</ul>
<hr>
<code>searchEvents(searchfor : dict, leveldict : dict) -> list[dict]</code>
<ul>
    <li> Returns a list of all events in <code>leveldict</code> that match all fields in <code>searchfor</code>.
    <li> For example, <blockquote> <code>searchfor={"eventType": "moveDecorations", "tag": "sampleTag"}</code></blockquote> will return a list of all <code>moveDecoration</code> events with tag <code>sampleTag</code>.
    <li> This function directly modifies <code>leveldict</code>.
</ul>
<hr>
<code>removeEvents(searchfor : dict, leveldict : dict) -> list[dict]</code>
<ul>
    <li>Similar to <code>searchEvents</code>, but removes all matching events.
    <li>This function returns a list of removed events.
    <li>This function directly modifies <code>leveldict</code>.
</ul>
<hr>
<code>replaceField(searchfor : dict, field : str, new, leveldict : dict) -> None</code>
<ul>
    <li>Searches for events in <code>leveldict</code> using <code>searchfor</code>, and replaces the value in <code>field</code> with <code>new</code>.
    <li>For example, <blockquote><code>replaceField({"eventType": "Flash", "duration": 0.5}, "startColor", "800080", leveldict)</code></blockquote> finds all <code>Flash</code> events with duration <code>0.5</code> and changes their start color to <code>#800080</code>. 
</ul>
<hr>
<code>writeToFile(leveldict : dict, filename : str) -> None</code>
<ul>
    <li>Writes the <code>leveldict</code> to the specified file.
</ul>
<hr><br><br><br><br>

