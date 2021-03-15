(* AppleScript to start OBS and turnn on the virtual camera.

Adapted from:
https://gist.github.com/iamkirkbater/ba6278d0ac6d695cb8c6c5fc309ba210

More discussion at: https://github.com/johnboiles/obs-mac-virtualcam/issues/132

*)

tell application "OBS" to activate
tell application "System Events"
	tell process "OBS"
		set frontmost to true
		click menu item "Start Virtual Camera" of menu "Tools" of menu bar 1
	end tell
end tell
