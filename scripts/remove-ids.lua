-- Strip heading identifiers so pandoc doesn't insert bookmark fields
-- that LibreOffice renders as visible [ ] bracket characters.
function Header(el)
  el.identifier = ""
  return el
end
