import sys
from util import *
import os
import string
import zlib

class strg(object):
	name = ""
	size = 0
	offset = 0
	def __init__(self, id):
		self.id = id

class nus3bank(object):
	contents = []
	propOffset = 0
	binfOffset = 0
	grpOffset = 0
	dtonOffset = 0
	toneOffset = 0
	junkOffset = 0
	packOffset = 0
	def __init__(self, size):
		self.size = size

class tone(object):
	name = ""
	ext = ""
	packOffset = 0
	size = 0
	def __init__(self, offset, metaSize):
		self.offset = offset
		self.metaSize = metaSize

nus3 = open(sys.argv[1], 'rb+')
if nus3.read(4) != "NUS3":
	nus3.seek(0)
	data = nus3.read()
	nus3_decom = zlib.decompress(data)
	nus3.close()
	nus3 = open(string.replace(sys.argv[1], ".nus3bank", "_decompressed.nus3bank"), "wb+")
	nus3.write(nus3_decom)
	nus3.seek(0)
	data = None
	nus3_decom = None
else:
	nus3.seek(0)
"""
if len(sys.argv) < 3:
	outfolder = string.replace(sys.argv[1], ".nus3bank", "")
else:
	outfolder = sys.argv[2]
if not os.path.exists(outfolder):
	os.mkdir(outfolder)
"""
assert nus3.read(4) == "NUS3"
size = readu32le(nus3)

bank = nus3bank(size)
assert nus3.read(8) == "BANKTOC ", "Not a bank archive!"
tocSize = readu32le(nus3)
contentCount = readu32le(nus3)
offset = 0x14 + tocSize
for i in range(contentCount):
	content = nus3.read(4)
	contentSize = readu32le(nus3)
	if content == "PROP":
		propOffset = offset
		propSize = contentSize
	elif content == "BINF":
		binfOffset = offset
		binfSize = contentSize
	elif content == "GRP ":
		grpOffset = offset
		grpSize = contentSize
	elif content == "DTON":
		dtonOffset = offset
		dtonSize = contentSize
	elif content == "TONE":
		toneOffset = offset
		toneSize = contentSize
	elif content == "JUNK":
		junkOffset = offset
		junkSize = contentSize
	elif content == "MARK":
		markOffset = offset
		markSize = contentSize
	elif content == "PACK":
		packOffset = offset
		packSize = contentSize
	else:
		print "Unknown content type " + content
	offset += 8 + contentSize

nus3.seek(binfOffset)
assert nus3.read(4) == "BINF"
assert readu32le(nus3) == binfSize
assert readu32le(nus3) == 0
assert readu32le(nus3) == 3
binfStringSize = readByte(nus3)
binfString = nus3.read(binfStringSize-1)
if len(sys.argv) < 3:
	outfolder = binfString
else:
	outfolder = sys.argv[2]
if not os.path.exists(outfolder):
	os.mkdir(outfolder)
nus3.seek(1,1)
#print binfString
padding = (binfStringSize + 1) % 4
#print padding
if padding == 0:
	pass
else:
	nus3.seek(abs(padding-4), 1)
nus3ID = readu32le(nus3)
#print hex(nus3ID)

nus3.seek(toneOffset)
assert nus3.read(4) == "TONE"
assert readu32le(nus3) == toneSize
toneCount = readu32le(nus3)
print "%s:%s:\"%s\"" % (nus3ID, hex(nus3ID), binfString)
tones = []
for i in range(toneCount):
	offset = readu32le(nus3) + toneOffset + 8
	metaSize = readu32le(nus3)
	tones.append(tone(offset, metaSize))
	
for i in range(toneCount):
	if tones[i].metaSize <= 0xc:
		continue
	nus3.seek(tones[i].offset+6)
	tempByte = readByte(nus3)
	if tempByte > 9 or tempByte == 0:
		nus3.seek(5, 1)
	else:
		nus3.seek(1,1)
	stringSize = readByte(nus3)
#	print hex(nus3.tell())
	tones[i].name = nus3.read(stringSize - 1)
	nus3.seek(1,1)
	print "\t" + hex(i) + ":" + tones[i].name
	padding = (stringSize + 1) % 4
	if padding == 0:
		nus3.seek(4, 1)
	else:
		nus3.seek(abs(padding-4) + 4, 1)
#	assert readu32le(nus3) == 8
	nus3.seek(4,1)
	tones[i].packOffset = readu32le(nus3)
	tones[i].size = readu32le(nus3)
	print(tones[i].packOffset)
#	print hex(tones[i].packOffset) + " - " + hex(tones[i].size)
	if tones[i].packOffset < 0xffffffff:
		nus3.seek(packOffset + 8 + tones[i].packOffset)
		tones[i].ext = ".idsp"

		outSound = open(outfolder + "/" + hex(i) + "-" + tones[i].name + tones[i].ext, "wb")
		outSound.write(nus3.read(tones[i].size))
		outSound.close()
	
nus3.close()