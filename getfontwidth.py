import unicodedata


text = "こんにちwa!！ｴ"
text_width = 0
for c in text :
  type = unicodedata.east_asian_width(c)
  if type == 'H' or type == 'Na':
    text_width += 1
  else :
    text_width += 2

print(text_width)
print(text)
bar = ""
for i in range(text_width) :
  bar += '-'
print(bar)
