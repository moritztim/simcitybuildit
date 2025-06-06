> Disclaimer:
> Most of the information in this repository is severely outdated.

# simcitybuildit
Documenting Simcity Buildit internals


The game is build upon the marmalade game engine.

in .apk files the main binary is in Simcity.s3e, this is a lzma compressed file, you can use 7zip to decompress it.
in .ipa file the s3e binary is embedded in the main executable, and scrambled somewhat. I'll post a decoder later.

The game data is in .group.bin files. These used to be lz4 compressed, ( `brew install lz4` for the decompressor ), however in the latest version they are now encrypted, as confirmed by no lz4 header and a high entropy. [DiE](https://github.com/horsicq/Detect-It-Easy) finds that most of the `.group.bin` files are raw deflate streams.

One intereting example i post here: [badwords.txt](badwords.txt).
reading through the list you find the usual profanity, but apparently also the 1989 Tiananmen Square massacre, or Tibettan independence are listed as 'badwords'. ( referred to as 'may 35th' - `5月35日`  or `5月35号` ). Part of the list seems to be in order of writing, so you can follow the author's train of thought. Here's some more intersting examples of "bad words" in order of appearance:
- gay
- jews
- capital
- affenarsch (monkey ass in german)
- antichrist
- assyria
- ast
- ballfondler
- revolution
- twitter
- xijinping
- sweaty balls
- hollywood

See [badwords.md](badwords.md) for a google-translated version.

# Random Info

 * [OmegaLayout.md](OmegaLayout.md) - optimal layouts for Controlnet Tower in Omega residential zones.
 * [AreaUpgrades.md](AreaUpgrades.md) - overview of cost of buying area extensions.
 
# Downloads

 * [decodecsv.py](decodecsv.py) - a script for decoding csv.group.bin, and other data files.

<details>
	<summary>group.bin format (outdated)</summary>

# group.bin format

The compressed files start with the magic bytes: `04 22 4d 18`.
The decompressed files start with the magic bytes: `3d 03 07 01 00 00 87 e0 81 80`.

In older .ipa's the fourth byte is zero instead of one.

| type      | content
| --------- | ------
|  10 bytes    | header magic
|  uint32    | filename length
|  bytes    | filename, followed by 9 bytes: `00 00 00 00 00 77 21 3c dc`
|  uint32   | total content size
|  uint32   | number of sections

## sections

| type      | content
| --------- | ------
|  uint32   | section magic
|  uint32   | number of blocks
|  2 bytes  | in all but one file: `01 01`
|  ...      | section data

Then followed by block data.

Each block starts with:

| type      | content
| --------- | ------
| uint32    | size, including this header
| uint32    | some checksum??
|  ...      | block content

## section types

|    magic |  meaning
| -------- | -----
| 2544f997 | contains color codes
| 3521f539 |  
| 62ab11c4 |  gpu code: <text>, <text>, [ <varname> <values> ]+
| 89546ed9 |
| 9b0704c1 | font path names  
| c6133cad |
| c61d838d | html
| d5610dab | audio
| e1ccaf5c |
| e1ccafe2 | 3d data
| f67cbd74 | database - named tables with records with named fields



## file type f67cbd74

| type      | content
| --------- | ------
|  uint32   | string count
|  bytes    | string table, each string has a uint16 length, followed by utf-8 encoded text.
|  uint32   | number of tables
|   ...     | table data
| 128 bytes | probably rsa signature

table layout:

| type      | content
| --------- | ------
|  string   | tablename
|  uint32   | number of fields per record
|  n strings  | field names
|  n bytes    | for each field the data type
|  uint32   | record count
|  ...      | record data

field types:

| type  | encoding |  meaning
| ----- | -------- | ----------
|   0   | uint16 | string, index into the string table at the start of this section.
|   1   | uint32 | number
|   2   | float32 | floating point number
|   3   | uint32  | color value
	
</details>

# network protocol

 * The initial url is: http://live.prod.simcitybuildit.com/simcity/
 * after login the user gets a new url to use, usually a numeric ip address, and confusingly (but not inconveniently) using http over port 443 
 * requests are either with POST or GET

 * on a rooted android device it is quite easy to capture the network trafic on the phone using tcpdump.
 * and inspect files in the `/data/data/com.ea.game.simcitymobile_row/files` directory for changes.

requests used:

|  request |  query   | POST data  | response
| -------- | --------- | --------- | --------
|  Login  | see below | *none* | player state
|  GetUpdates  | see below | sc-list of protobuf encoded filenames | sc-list of protobuf encoded file info
|  GetPlayer | see below, `ids` contains playerid | *none* | sc encoded player state
|  Ping  | see below | *none* | sc encoded response
|  SetPlayer | see below | sc encoded gzipped protobuf encoded streams | sc encoded response
|  Log |  device spec | json data | *none*
|  TextRender |  *none*  | protobuf containing texts | gzipped protobuf containing pngs
|  GetMarket | see below | *none* | ...
|  Initialize | `key` | *none* | 128 byte key/sig(?), stamp, uid, 20byte hmac
|  LogError | `p` | json data | *none*
|  Competition | see below | sc encoded protobuf | sc encoded response
|  GetFriendMeta | see below | sc encoded protobuf | sc encoded response


## request query parameters

commonly used query parameters

| arg | description
| --- | ----------
| app   | the app version number
| id    | the user id
| keyid | '2'
| req   | request timestamp
| sig   | hmac of request (?)
| usesid | session timestamp
| nw    | 'G' or 'W'
| p     | '2'
| lvl   | current player level
| fw    | current android / ios version
| df    | '14'
| gpuid  | your device's GPU type
| devid | your device model name
| retina | '1'

## sc encoding

This is not entirely clear yet.

Responses start with a varint ( see protobuf ) containing a timestamp.
followed by a list of type + values, with optional length.
some of these values are gzipped or uncompressed protobuf encoded structures.

| type | content
| ---- | -------
|  05  | baseurl
|  08  | three varints |  two of which are timestamps, probably a validity period
|  06  | varint  | timestamp
| 0c, od, 0f | three varints + gzipped data | 
| 20, 24, 2a | varint + protobuf

## the hmac

The secret key for the hmac is stored in the userdata area in a file named `appdata.i3d`.
This key is scrambled somewhat before use.
I think it is updated with every request, so if you want to automate some things in SC you would have to do
this on the device running the game. because you do need the actual appdata.i3d file contents, and update it your self then.

the exact details I still need to figure out.

# local storage

on android the local game storage is in `/data/data/com.ea.game.simcitymobile_row/files/`.

## 0.pb

contains the game state, in a packet similar to the Login or SetPlayer responses.

## 64.pb

contains protobuf encoded data

## 65.pb

contains a protobuf encoded activity log,
I think this is so the simcity app can playback your game activity after some offline time.

## 67.pb

inapp purchase items

