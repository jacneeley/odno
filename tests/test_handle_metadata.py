import pytest
import datetime
import os

from collections import deque
from unittest.mock import Mock, patch, call

from src import handle_metadata

last_fm_test = {"album":{"artist":"Sonic Youth","mbid":"01c1cbdd-f920-4dcb-9377-9ae69f08158a","tags":{"tag":[{"url":"https:\\\\www.last.fm\\tag\\alternative","name":"alternative"},{"url":"https:\\\\www.last.fm\\tag\\alternative+rock","name":"alternative rock"},{"url":"https:\\\\www.last.fm\\tag\\noise+rock","name":"noise rock"},{"url":"https:\\\\www.last.fm\\tag\\experimental","name":"experimental"},{"url":"https:\\\\www.last.fm\\tag\\post-punk","name":"post-punk"}]},"playcount":"17768902","image":[{"size":"small","#text":"https:\\\\lastfm.freetls.fastly.net\\i\\u\\34s\\dce45912d7401e62d0e9298fd731e667.jpg"},{"size":"medium","#text":"https:\\\\lastfm.freetls.fastly.net\\i\\u\\64s\\dce45912d7401e62d0e9298fd731e667.jpg"},{"size":"large","#text":"https:\\\\lastfm.freetls.fastly.net\\i\\u\\174s\\dce45912d7401e62d0e9298fd731e667.jpg"},{"size":"extralarge","#text":"https:\\\\lastfm.freetls.fastly.net\\i\\u\\300x300\\dce45912d7401e62d0e9298fd731e667.jpg"},{"size":"mega","#text":"https:\\\\lastfm.freetls.fastly.net\\i\\u\\300x300\\dce45912d7401e62d0e9298fd731e667.jpg"},{"size":"","#text":"https:\\\\lastfm.freetls.fastly.net\\i\\u\\300x300\\dce45912d7401e62d0e9298fd731e667.jpg"}],"tracks":{"track":[{"streamable":{"fulltrack":"0","#text":"0"},"duration":339,"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\\Dirty+Boots","name":"Dirty Boots","@attr":{"rank":1},"artist":{"url":"https:\\\\www.last.fm\\music\\Sonic+Youth","name":"Sonic Youth","mbid":"5cbef01b-cc35-4f52-af7b-d0df0c4f61b9"}},{"streamable":{"fulltrack":"0","#text":"0"},"duration":377,"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\\Tunic+(Song+for+Karen)","name":"Tunic (Song for Karen)","@attr":{"rank":2},"artist":{"url":"https:\\\\www.last.fm\\music\\Sonic+Youth","name":"Sonic Youth","mbid":"5cbef01b-cc35-4f52-af7b-d0df0c4f61b9"}},{"streamable":{"fulltrack":"0","#text":"0"},"duration":188,"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\\Mary-Christ","name":"Mary-Christ","@attr":{"rank":3},"artist":{"url":"https:\\\\www.last.fm\\music\\Sonic+Youth","name":"Sonic Youth","mbid":"5cbef01b-cc35-4f52-af7b-d0df0c4f61b9"}},{"streamable":{"fulltrack":"0","#text":"0"},"duration":246,"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\\Kool+Thing","name":"Kool Thing","@attr":{"rank":4},"artist":{"url":"https:\\\\www.last.fm\\music\\Sonic+Youth","name":"Sonic Youth","mbid":"5cbef01b-cc35-4f52-af7b-d0df0c4f61b9"}},{"streamable":{"fulltrack":"0","#text":"0"},"duration":202,"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\\Mote","name":"Mote","@attr":{"rank":5},"artist":{"url":"https:\\\\www.last.fm\\music\\Sonic+Youth","name":"Sonic Youth","mbid":"5cbef01b-cc35-4f52-af7b-d0df0c4f61b9"}},{"streamable":{"fulltrack":"0","#text":"0"},"duration":138,"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\\My+Friend+Goo","name":"My Friend Goo","@attr":{"rank":6},"artist":{"url":"https:\\\\www.last.fm\\music\\Sonic+Youth","name":"Sonic Youth","mbid":"5cbef01b-cc35-4f52-af7b-d0df0c4f61b9"}},{"streamable":{"fulltrack":"0","#text":"0"},"duration":308,"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\\Disappearer","name":"Disappearer","@attr":{"rank":7},"artist":{"url":"https:\\\\www.last.fm\\music\\Sonic+Youth","name":"Sonic Youth","mbid":"5cbef01b-cc35-4f52-af7b-d0df0c4f61b9"}},{"streamable":{"fulltrack":"0","#text":"0"},"duration":132,"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\\Mildred+Pierce","name":"Mildred Pierce","@attr":{"rank":8},"artist":{"url":"https:\\\\www.last.fm\\music\\Sonic+Youth","name":"Sonic Youth","mbid":"5cbef01b-cc35-4f52-af7b-d0df0c4f61b9"}},{"streamable":{"fulltrack":"0","#text":"0"},"duration":350,"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\\Cinderella%27s+Big+Score","name":"Cinderella's Big Score","@attr":{"rank":9},"artist":{"url":"https:\\\\www.last.fm\\music\\Sonic+Youth","name":"Sonic Youth","mbid":"5cbef01b-cc35-4f52-af7b-d0df0c4f61b9"}},{"streamable":{"fulltrack":"0","#text":"0"},"duration":60,"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\\Scooter+And+Jinx","name":"Scooter And Jinx","@attr":{"rank":10},"artist":{"url":"https:\\\\www.last.fm\\music\\Sonic+Youth","name":"Sonic Youth","mbid":"5cbef01b-cc35-4f52-af7b-d0df0c4f61b9"}},{"streamable":{"fulltrack":"0","#text":"0"},"duration":None,"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\\Titanium+Expose","name":"Titanium Expose","@attr":{"rank":11},"artist":{"url":"https:\\\\www.last.fm\\music\\Sonic+Youth","name":"Sonic Youth","mbid":"5cbef01b-cc35-4f52-af7b-d0df0c4f61b9"}}]},"url":"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo","name":"Goo","listeners":"1065324","wiki":{"published":"10 Oct 2022, 17:41","summary":"Goo is the sixth full-length studio album by American alternative rock band Sonic Youth, released on June 26, 1990 by DGC Records. For this album, the band sought to expand upon its trademark alternating guitar arrangements and the layered sound of their previous album Daydream Nation (1988) with songwriting on that was more topical than past works, exploring themes of female empowerment and pop culture. Coming off the success of Daydream Nation, Nick Sansano returned to engineer Goo, but veteran producer Ron Saint Germain was chosen by Sonic Youth to finish mixing the album following Sansano's dismissal. Goo was a <a href=\"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\">Read more on Last.fm<\\a>.","content":"Goo is the sixth full-length studio album by American alternative rock band Sonic Youth, released on June 26, 1990 by DGC Records. For this album, the band sought to expand upon its trademark alternating guitar arrangements and the layered sound of their previous album Daydream Nation (1988) with songwriting on that was more topical than past works, exploring themes of female empowerment and pop culture. Coming off the success of Daydream Nation, Nick Sansano returned to engineer Goo, but veteran producer Ron Saint Germain was chosen by Sonic Youth to finish mixing the album following Sansano's dismissal.\n\nGoo was a critical and commercial success upon its release, peaking at number 96 on the US Billboard 200, their highest chart position to date. Although it lacked significant radio airplay, its lead single \"Kool Thing\", a collaborative effort with Public Enemy's Chuck D, reached number seven on the Billboard Modern Rock Tracks chart. Since then, Goo has been viewed as one of alternative rock's most important albums, and is considered musically and artistically significant. In 2020, the album was ranked at number 358 on Rolling Stone's 500 greatest albums of all time list.\n\nIn 1989, nearly a year after the release of the band's breakthrough album Daydream Nation, Sonic Youth announced that it had signed a recording contract with Geffen Records, the group's first major label deal. Sonic Youth decided to sever relations with its former label, Enigma Records, as a result of the band's displeasure with Enigma's indecisive marketing and distribution of Daydream Nation, as well as \"Teen Age Riot\"—‌the album's accompanying single. Another factor that contributed to the group's departure from the label was Enigma's handling of The Whitey Album, an experimental album of sound manipulation and hip-hop influences released under the name Ciccone Youth. Not only did Enigma reject the band's proposal to simultaneously release the album with Daydream Nation, the label's publicity branch also attempted to withdraw its cover art—an enlarged photo of Madonna's face—even though Madonna reportedly gave Sonic Youth her permission to use it.\n\nBy mid-1989, Sonic Youth's relationship with its British and American label head Paul Smith, who the band's legal counsel, Richard Grebal, termed \"a trusted advisor but never a manager\", was growing increasingly strained. Tensions between Smith and the group had begun in 1986 when Smith arranged the release of live recordings by the band on the album Walls Have Ears without their input. Mindful about their work and image, Sonic Youth was irritated by the decision, especially when the album was distributed before Evol. The situation was compounded further when Smith took a bold negotiating stance with major record labels during the Daydream Nation tour and took long intervals to communicate information to the band. His stance, which had the potential to scare away record executives, represented the final straw for the band. On June 2, 1989, Sonic Youth went to Smith's apartment, ostensibly to discuss another music video for Daydream Nation, to announce an end to their partnership.\n\nHaving entertained offers from A&M Records, Atlantic Records, and Mute Records, Sonic Youth signed a five-album deal worth $300,000 with a clause which secured the band's complete control of its creative output. The group, however, was somewhat dissatisfied that the album would not be released by Geffen but rather a new and unestablished subsidiary label, DGC Records. <a href=\"https:\\\\www.last.fm\\music\\Sonic+Youth\\Goo\">Read more on Last.fm<\\a>. User-contributed text is available under the Creative Commons By-SA License; additional terms may apply."}}}
discogs_test = {'id': 9768, 'main_release': 1352572, 'most_recent_release': 30192461, 'resource_url': 'https://api.discogs.com/masters/9768', 'uri': 'https://www.discogs.com/master/9768-Sonic-Youth-Daydream-Nation', 'versions_url': 'https://api.discogs.com/masters/9768/versions', 'main_release_url': 'https://api.discogs.com/releases/1352572', 'most_recent_release_url': 'https://api.discogs.com/releases/30192461', 'num_for_sale': 580, 'lowest_price': 4.53, 'images': [{'type': 'primary', 'uri': 'https://i.discogs.com/WFA7Kod1I11LlmFF9Y8pU-uwf1yS58cutjotHKDdAKs/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzU1/Mi00OTYyLmpwZWc.jpeg', 'resource_url': 'https://i.discogs.com/WFA7Kod1I11LlmFF9Y8pU-uwf1yS58cutjotHKDdAKs/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzU1/Mi00OTYyLmpwZWc.jpeg', 'uri150': 'https://i.discogs.com/oH7S7aPUTy_Ooim8OvELwl4xkFr-9q0_XzVQKqosgYI/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzU1/Mi00OTYyLmpwZWc.jpeg', 'width': 600, 'height': 600}, {'type': 'secondary', 'uri': 'https://i.discogs.com/JiWUElNabpCvVH9Ik1VsFo_zRu-5FyI9tabxZJWBoLs/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzU3/Ny0xNTQxLmpwZWc.jpeg', 'resource_url': 'https://i.discogs.com/JiWUElNabpCvVH9Ik1VsFo_zRu-5FyI9tabxZJWBoLs/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzU3/Ny0xNTQxLmpwZWc.jpeg', 'uri150': 'https://i.discogs.com/4r-CSHTGEkJQ972Jz4KKDnTmO3XdycIFncdOwNCcDso/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzU3/Ny0xNTQxLmpwZWc.jpeg', 'width': 600, 'height': 600}, {'type': 'secondary', 'uri': 'https://i.discogs.com/89m0pitlISAz2DzZSkR7pzeC_UEtdYpQERG7LeZEFvM/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzU5/MC0xNjc3LmpwZWc.jpeg', 'resource_url': 'https://i.discogs.com/89m0pitlISAz2DzZSkR7pzeC_UEtdYpQERG7LeZEFvM/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzU5/MC0xNjc3LmpwZWc.jpeg', 'uri150': 'https://i.discogs.com/K5ccXW0_Nigp0Nr_FSpTwz8iBUHFhy8lAPo7XPl_Lsw/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzU5/MC0xNjc3LmpwZWc.jpeg', 'width': 600, 'height': 600}, {'type': 'secondary', 'uri': 'https://i.discogs.com/HsOm2cOKpI0e3ee1vNRTt30nXyI-h4nQ0p1I3EcqtD0/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzYw/Ny05MDA0LmpwZWc.jpeg', 'resource_url': 'https://i.discogs.com/HsOm2cOKpI0e3ee1vNRTt30nXyI-h4nQ0p1I3EcqtD0/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzYw/Ny05MDA0LmpwZWc.jpeg', 'uri150': 'https://i.discogs.com/ACHUuqU5GOhajFPjyskwo8yZVcJezHW_AtNBPeoZw1k/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzYw/Ny05MDA0LmpwZWc.jpeg', 'width': 600, 'height': 600}, {'type': 'secondary', 'uri': 'https://i.discogs.com/FF6YCETiraBvUg8bfaIvfrWSCu5TL4QczwxkLpIgI5g/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzYy/My0zMTQwLmpwZWc.jpeg', 'resource_url': 'https://i.discogs.com/FF6YCETiraBvUg8bfaIvfrWSCu5TL4QczwxkLpIgI5g/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzYy/My0zMTQwLmpwZWc.jpeg', 'uri150': 'https://i.discogs.com/1wkXjt_pvtBoDl0ZO-HNsgohBIxbo8YEwKa29DqjJ4I/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzYy/My0zMTQwLmpwZWc.jpeg', 'width': 600, 'height': 600}, {'type': 'secondary', 'uri': 'https://i.discogs.com/En0I7AAasno71ckPJdOU7f7MEMMLHihr802ekKBUHPU/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzY2/Ny0yMDk0LmpwZWc.jpeg', 'resource_url': 'https://i.discogs.com/En0I7AAasno71ckPJdOU7f7MEMMLHihr802ekKBUHPU/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzY2/Ny0yMDk0LmpwZWc.jpeg', 'uri150': 'https://i.discogs.com/4PBudWZFTVSVrw80v7Bvfz48Wvs8PkZ2GBiBzdmU56s/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzY2/Ny0yMDk0LmpwZWc.jpeg', 'width': 600, 'height': 600}, {'type': 'secondary', 'uri': 'https://i.discogs.com/UJwU_15WcZ1B47BdDAor3CJVvt0VC5p1-j03jbv_06A/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzY4/Ni0yMjY0LmpwZWc.jpeg', 'resource_url': 'https://i.discogs.com/UJwU_15WcZ1B47BdDAor3CJVvt0VC5p1-j03jbv_06A/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzY4/Ni0yMjY0LmpwZWc.jpeg', 'uri150': 'https://i.discogs.com/3qv9SmOEZG_MXsdBZpY1O00rJpC2P48m-WIp44GfVO4/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzY4/Ni0yMjY0LmpwZWc.jpeg', 'width': 600, 'height': 600}, {'type': 'secondary', 'uri': 'https://i.discogs.com/Nu6Qx7pC1LMOfoZKO6Tzj_dVAZOfsdTncTCFi7iYIQ8/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3Nzcw/MC0xOTA5LmpwZWc.jpeg', 'resource_url': 'https://i.discogs.com/Nu6Qx7pC1LMOfoZKO6Tzj_dVAZOfsdTncTCFi7iYIQ8/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3Nzcw/MC0xOTA5LmpwZWc.jpeg', 'uri150': 'https://i.discogs.com/c6SRgDYkGEje49k0iZJtw6OppkpTmJ0ax9uxTLKfLHs/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3Nzcw/MC0xOTA5LmpwZWc.jpeg', 'width': 600, 'height': 600}, {'type': 'secondary', 'uri': 'https://i.discogs.com/dPvhsXeViHkl4Eo3qje3ECmA2wWcmqkVsTkcCRkUuEk/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3Nzcz/MC00NDkxLmpwZWc.jpeg', 'resource_url': 'https://i.discogs.com/dPvhsXeViHkl4Eo3qje3ECmA2wWcmqkVsTkcCRkUuEk/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3Nzcz/MC00NDkxLmpwZWc.jpeg', 'uri150': 'https://i.discogs.com/OJVFbMXOCwHew3pZ7xp--5Ji9qScBq2rzGp4oPR9y-U/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3Nzcz/MC00NDkxLmpwZWc.jpeg', 'width': 600, 'height': 600}], 'genres': ['Rock'], 'styles': ['Alternative Rock', 'Indie Rock', 'Avantgarde', 'Noise Rock'], 'year': 1988, 'tracklist': [{'position': 'A1', 'type_': 'track', 'title': 'Teen Age Riot', 'extraartists': [{'name': 'Kim Gordon', 'anv': '', 'join': '', 'role': 'Vocals [Intro]', 'tracks': '', 'id': 187676, 'resource_url': 'https://api.discogs.com/artists/187676'}], 'duration': '6:56'}, {'position': 'A2', 'type_': 'track', 'title': 'Silver Rocket', 'duration': '3:46'}, {'position': 'A3', 'type_': 'track', 'title': 'The Sprawl', 'duration': '7:39'}, {'position': 'B1', 'type_': 'track', 'title': "'Cross The Breeze", 'duration': '7:00'}, {'position': 'B2', 'type_': 'track', 'title': "Eric's Trip", 'duration': '3:46'}, {'position': 'B3', 'type_': 'track', 'title': 'Total Trash', 'duration': '7:30'}, {'position': 'C1', 'type_': 'track', 'title': 'Hey Joni', 'duration': '4:17'}, {'position': 'C2', 'type_': 'track', 'title': 'Providence', 'extraartists': [{'name': 'Thurston Moore', 'anv': '', 'join': '', 'role': 'Piano', 'tracks': '', 'id': 2108, 'resource_url': 'https://api.discogs.com/artists/2108'}, {'name': 'Mike Watt', 'anv': '', 'join': '', 'role': 'Voice [Answering Machine]', 'tracks': '', 'id': 77192, 'resource_url': 'https://api.discogs.com/artists/77192'}], 'duration': '2:39'}, {'position': 'C3', 'type_': 'track', 'title': 'Candle', 'duration': '4:57'}, {'position': 'C4', 'type_': 'track', 'title': 'Rain King', 'duration': '4:38'}, {'position': 'D1', 'type_': 'track', 'title': 'Kissability', 'duration': '3:06'}, {'position': 'D2A', 'type_': 'track', 'title': 'Trilogy: a) The Wonder', 'duration': '4:27'}, {'position': 'D2B', 'type_': 'track', 'title': 'Trilogy: b) Hyperstation', 'duration': '7:04'}, {'position': 'D2Z', 'type_': 'track', 'title': 'Trilogy: z) Eliminator Jr.', 'duration': '2:37'}], 'artists': [{'name': 'Sonic Youth', 'anv': '', 'join': '', 'role': '', 'tracks': '', 'id': 17199, 'resource_url': 'https://api.discogs.com/artists/17199', 'thumbnail_url': 'https://i.discogs.com/6mgDJfl-HTgb3pgyUCDKEESG9W5ghbbIGk01ZsSE-QQ/rs:fit/g:sm/q:90/h:400/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9BLTE3MTk5/LTE2MDA1NTc0NjYt/NzI3NC5qcGVn.jpeg'}], 'title': 'Daydream Nation', 'notes': 'LP Masters:\r\n1988 Masterdisk DMM is found on 1988 releases worldwide and all Blast First represses.\r\n2007 Golden mastering for the box set is repressed in 2014 2xLP version.\r\n\r\nCD Masters:\r\n1988 Masterdisk version heard on all worldwide 1988 releases.\r\n1993 Remaster (uncredited) heard on all DGC/Geffen versions including except Deluxe Edition.\r\n2007 Golden remaster is found on deluxe edition and 2014 CD.\r\n\r\n\'Daydream Nation\' was Sonic Youth’s sixth full-length, their first double-LP, and their last for an indie label before signing with Geffen.\r\n\r\nWidely considered to be their watershed moment, the album catapulted them into the mainstream and proved that indie bands could enjoy wider commercial success without compromising their artistic vision.\r\n\r\nMore recently, has been recognized as a classic of its era: \'Pitchfork\' ranked it #1 on their “100 Greatest Albums of the 1980s”; \'Spin\' listed it at #13 on their “125 Best Albums of 1985-2010”. Daydream Nation was one of 50 recordings chosen by the Library Of Congress to be added to the National Recording Registry in 2006 and it was voted "One Of The Greatest Albums Of All Time" by \'Rolling Stone\'.\r\n', 'data_quality': 'Correct', 'videos': [{'uri': 'https://www.youtube.com/watch?v=tPytYrYqDbA', 'title': 'Sonic Youth - Teenage Riot', 'description': 'Music Video for "Teenage Riot" off the album Daydream Nation. \nDir. Sonic Youth', 'duration': 260, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=viF12Mu3-5w', 'title': 'Sonic Youth - Silver Rocket (Restored)', 'description': "'Silver Rocket' comes from Sonic Youth's album 'Daydream Nation.'\nListen to the full album: http://smarturl.it/SY_DaydreamNation\n\nConnect with Sonic Youth: \nhttp://sonicyouth.com/\nhttps://www.facebook.com/sonicyouth/\nhttps://twitter.com/thesonicyouth", 'duration': 211, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=x9r0renJWuY', 'title': 'Teen Age Riot', 'description': 'Provided to YouTube by TuneCore\n\nTeen Age Riot · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 419, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=wWTkb1xVin0', 'title': 'Silver Rocket', 'description': 'Provided to YouTube by TuneCore\n\nSilver Rocket · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 228, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=t6QW1KcDV8M', 'title': 'The Sprawl', 'description': 'Provided to YouTube by TuneCore\n\nThe Sprawl · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 463, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=wzsjWKVAy2Q', 'title': "'Cross the Breeze", 'description': "Provided to YouTube by TuneCore\n\n'Cross the Breeze · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.", 'duration': 421, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=_mu7MV_7aYs', 'title': "Eric's Trip", 'description': "Provided to YouTube by TuneCore\n\nEric's Trip · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.", 'duration': 229, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=qA0iUNAAixU', 'title': 'Total Trash', 'description': 'Provided to YouTube by TuneCore\n\nTotal Trash · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 454, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=FWa21X6Wu_s', 'title': 'Hey Joni', 'description': 'Provided to YouTube by TuneCore\n\nHey Joni · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 264, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=e32CMDyY2gc', 'title': 'Providence', 'description': 'Provided to YouTube by TuneCore\n\nProvidence · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 162, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=pQ1Ooe3_pIY', 'title': 'Candle', 'description': 'Provided to YouTube by TuneCore\n\nCandle · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 300, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=1kg24Ijsyhs', 'title': 'Rain King', 'description': 'Provided to YouTube by TuneCore\n\nRain King · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 280, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=nbWaT9XMH18', 'title': 'Kissability', 'description': 'Provided to YouTube by TuneCore\n\nKissability · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 188, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=Ez8faRV0r14', 'title': 'A) the Wonder', 'description': 'Provided to YouTube by TuneCore\n\nA) the Wonder · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 256, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=THarNd-jhgo', 'title': 'B) Hyperstation', 'description': 'Provided to YouTube by TuneCore\n\nB) Hyperstation · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 433, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=pNPp9lfzRzY', 'title': 'Z) Eliminator, Jr.', 'description': 'Provided to YouTube by TuneCore\n\nZ) Eliminator, Jr. · Sonic Youth\n\nDaydream Nation (Remastered Original Album)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-11\n\nAuto-generated by YouTube.', 'duration': 158, 'embed': True}, {'uri': 'https://www.youtube.com/watch?v=_K1ogOk4ITk', 'title': 'Within You Without You', 'description': 'Provided to YouTube by TuneCore\n\nWithin You Without You · Sonic Youth\n\nDaydream Nation (Deluxe Edition)\n\n℗ 1988 Squeaky Squawk\n\nReleased on: 1988-10-04\n\nAuto-generated by YouTube.', 'duration': 298, 'embed': True}]}

@pytest.mark.parametrize("platform, test_album, expected",
    [
        (
            "LASTFM",
            last_fm_test,
            {"album": "Goo", "artist": "Sonic Youth", "release_date" : datetime.datetime(1990, 6, 26, 0, 0)}
        ),
        (
            "DISCOGS",
            discogs_test,
            {"album": "Daydream Nation", "artist": "Sonic Youth", "release_date" : 1988}
        )
    ])
def test_check_album(platform, test_album, expected):
    '''
        Test check_album().
    '''
    assert expected == handle_metadata.check_album(test_album, platform)

@pytest.mark.parametrize("album, resp, expected_count, expected_song_attr",[
    (
        #album
        {"album": "Daydream Nation", "artist": "Sonic Youth", "release_date" : 1988},
        
        #resp
        {
            'images': [{'uri': 'https://example.com/cover.jpg'}],
            'styles': ['Alternative Rock', 'Indie Rock'],
            'genres': ['Rock'],
            'tracklist': [
                {'title': 'Teen Age Riot'},
                {'title': 'Silver Rocket'},
                {'title': 'The Sprawl'}
            ],
            'year': 1988
        },
        
        # number of tracks
        3,

        #expected attributes for track 1
        {
            'title': 'Teen Age Riot',
            'artist': 'Sonic Youth',
            'album_artist': 'Sonic Youth',
            'album': 'Daydream Nation',
            'cd': 1,
            'genre': 'Alternative Rock',
            'year': 1988,
            'track_num': 1,
            'cover': 'https://example.com/cover.jpg'
        }
    ),
    (
        {"album": "Goo", "artist": "Sonic Youth", "release_date": 1990},
        {
            'images': [{'uri': 'https://example.com/goo_cover.jpg'}],
            'styles': [],  # empty styles
            'genres': ['Alternative Rock'],
            'tracklist': [
                {'title': 'Dirty Boots'},
                {'title': 'Tunic (Song for Karen)'}
            ],
            'year': 1990
        },
        2,
        {
            'title': 'Dirty Boots',
            'artist': 'Sonic Youth',
            'album_artist': 'Sonic Youth',
            'album': 'Goo',
            'cd': 1,
            'genre': 'Alternative Rock',  # falls back to genres since styles is empty
            'year': 1990,
            'track_num': 1,
            'cover': 'https://example.com/goo_cover.jpg'
        }
    ),
    (
        #dummy album
        {"album": "Daydream Nation", "artist": "Sonic Youth", "release_date" : 1988},

        #dummy response
        discogs_test,
        
        #tracks
        14,
        
        # dummy object
        {
            'title': 'Teen Age Riot',
            'artist': 'Sonic Youth',
            'album_artist': 'Sonic Youth',
            'album': 'Daydream Nation',
            'cd': 1,
            'genre': 'Alternative Rock',
            'year': 1988,
            'track_num': 1,
            'cover': 'https://i.discogs.com/WFA7Kod1I11LlmFF9Y8pU-uwf1yS58cutjotHKDdAKs/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzU1/Mi00OTYyLmpwZWc.jpeg'
        }
    )
])
@patch('src.handle_metadata.Song')
def test_get_album_data_from_discogs(mock_song_class, album, resp, expected_count, expected_song_attr):
    '''
        Test get_album_data_from_discogs with mocked Song class.
    '''

    mock_song = Mock()
    mock_song_class.return_value = mock_song

    result = handle_metadata.get_album_data_from_discogs(album, resp, debug=False)

    assert mock_song_class.call_count == expected_count

    expected_calls = []
    for i , track in enumerate(resp['tracklist']):
        expected_attrs = expected_song_attr.copy()
        expected_attrs['title'] = track['title']
        expected_attrs['track_num'] = i + 1
        expected_calls.append(call(**expected_attrs))

    mock_song_class.assert_has_calls(expected_calls)
    
    assert len(result) == expected_count
    assert all(song == mock_song for song in result)

@pytest.mark.parametrize("album, resp, expected_count, expected_song_attr",[
    (
        #album
        {"album": "Goo", "artist": "Sonic Youth", "release_date" : "1990-06-26 00:00:00"},
        
        #dummy response from lastfm api
        {
            "album" : {
                "artist" : "Sonic Youth",
                "tags" : { "tag" : [{ "name" : "Alternative Rock" }] },
                "image" : [
                        { "#text": "dummylink"},
                        { "#text": "dummylink2" },
                        { "#text": "dummylink3" },
                        {"#text" : "https://example.com/goo_cover.jpg"}
                    ],
                "tracks" : { 
                        "track" : [
                            {"name" : "Dirty Boots"} , { "name" : "Tunic (Song for Karen)" }]
                    },
                "name" : "Goo"
            }
        },
        
        # number of tracks
        2,
        
        #expected attributes for track 1
        {
            'title': 'Dirty Boots',
            'artist': 'Sonic Youth',
            'album_artist': 'Sonic Youth',
            'album': 'Goo',
            'cd': 1,
            'genre': 'Alternative Rock',
            'year': "1990-06-26 00:00:00",
            'track_num': 1,
            'cover': 'https://example.com/goo_cover.jpg'
        }
    ),
    (

        #dummy album
        {"album": "Daydream Nation", "artist": "Sonic Youth", "release_date" : "1988-01-01 00:00:00"},
        
        # dummy response
        {
            "album" : {
                "artist" : "Sonic Youth",
                "tags" : { "tag" : [{ "name" : "Noise Rock" }] },
                "image" : [
                        { "#text": "dummylink"},
                        { "#text": "dummylink2" },
                        { "#text": "dummylink3" },
                        {"#text" : "https://example.com/goo_cover.jpg"}
                    ],
                "tracks" : { 
                        "track" : [
                            {"name" : "Teenage Riot"} , { "name" : "Silver Rocket" }, { "name" : "The Sprawl" }]
                    },
                "name" : "Goo"
            }
        },
        #number of tracks
        3,
        
        # mock song object
        {
            'title': 'Teenage Riot',
            'artist': 'Sonic Youth',
            'album_artist': 'Sonic Youth',
            'album': 'Daydream Nation',
            'cd': 1,
            'genre': 'Noise Rock',
            'year': "1988-01-01 00:00:00",
            'track_num': 1,
            'cover': 'https://example.com/goo_cover.jpg'
        }
    ),
    (
        #dummy album
        {"album": "Goo", "artist": "Sonic Youth", "release_date" : "1992-06-26 00:00:00"},

        #dummy response
        last_fm_test,
        
        #tracks
        11,
        
        # dummy object
        {
            'title': 'Dirty Boots',
            'artist': 'Sonic Youth',
            'album_artist': 'Sonic Youth',
            'album': 'Goo',
            'cd': 1,
            'genre': 'alternative',
            'year': "1992-06-26 00:00:00",
            'track_num': 1,
            'cover': 'https:\\\\lastfm.freetls.fastly.net\\i\\u\\300x300\\dce45912d7401e62d0e9298fd731e667.jpg'
        }
    )
])
@patch('src.handle_metadata.Song')
def test_get_album_data_from_lastfm(mock_song_class, album, resp, expected_count, expected_song_attr):
    '''
    Test get_album_data_from_lastfm.
    '''
    mock_song = Mock()
    mock_song_class.return_value = mock_song

    result = handle_metadata.get_album_data_from_lastfm(album, resp, debug=False)

    assert mock_song_class.call_count == expected_count

    expected_calls = []
    for i , track in enumerate(resp['album']['tracks']['track']):
        expected_attrs = expected_song_attr.copy()
        expected_attrs['title'] = track['name']
        expected_attrs['track_num'] = i + 1
        expected_calls.append(call(**expected_attrs))

    mock_song_class.assert_has_calls(expected_calls)
    
    assert len(result) == expected_count
    assert all(song == mock_song for song in result)

@pytest.mark.parametrize("inputs, expected_result, mock_resp, mock_album, mock_songs", [
    (
        # Test case 1: User says yes to manual search and yes to correct album
        ["y", "Sonic Youth", "Daydream Nation", "y"],
        ["song1", "song2"],  # Expected return value (list of Song objects)
        {"mock": "lastfm_response"},  # Mock response from get_album_lastfm
        {"album": "Daydream Nation", "artist": "Sonic Youth"},  # Mock album from check_album
        ["song1", "song2"]  # Mock songs from get_album_data_from_lastfm
    ),
    (
        # Test case 2: User says yes to manual search but no to correct album
        ["y", "Sonic Youth", "Goo", "n"],
        [],  # Expected return value (empty list)
        {"mock": "lastfm_response"},
        {"album": "Goo", "artist": "Sonic Youth"},
        None  # Not used because get_album_data_from_lastfm won't be called
    ),
    (
        # Test case 3: User says no to manual search
        ["n"],
        [],  # Expected return value (empty list)
        None,  # Not used
        None,  # Not used
        None   # Not used
    ),
    (
        # Test case 4: User enters invalid input
        ["  ", "Sonic Youth", "Daydream Nation", "y"],
        [],
        {"mock": "lastfm_response"},
        {"album": "Daydream Nation", "artist": "Sonic Youth"},
        ["song1", "song2"]
    )
])
@patch('src.handle_metadata.prompts.wow_niche')
@patch('src.handle_metadata.get_album_data_from_lastfm')
@patch('src.handle_metadata.check_album')
@patch('src.handle_metadata.fetcher.get_album_lastfm')
@patch('builtins.input')
def test_manual_search_gets_track_list(mock_input, mock_get_album_lastfm, mock_check_album,
                                       mock_get_album_data, mock_niche_prompt, inputs, expected_result,
                                       mock_resp, mock_album, mock_songs):
    '''
    Test manual_search with various user inputs
    '''

    mock_input.side_effect = inputs

    #external dependencies
    mock_get_album_lastfm.return_value = mock_resp
    mock_check_album.return_value = mock_album
    mock_get_album_data.return_value = mock_songs

    #call function
    result = handle_metadata.manual_search()

    assert result == expected_result

    # verify calls
    if inputs[0].lower() == "y":
        mock_get_album_lastfm.assert_called_once_with(inputs[1], inputs[2], True)

        mock_check_album.assert_called_once_with(mock_resp, "LASTFM")

        if inputs[3].lower() == "y":
            mock_get_album_data.assert_called_once_with(mock_album, mock_resp, True)
            mock_niche_prompt.assert_not_called()
        else:
            mock_get_album_data.assert_not_called()
            mock_niche_prompt.assert_called_once()

    else:
        #no external calls
        mock_get_album_lastfm.assert_not_called()
        mock_check_album.assert_not_called()
        mock_get_album_data.assert_not_called()
        mock_niche_prompt.assert_not_called()

@pytest.mark.parametrize("inputs, expected_result, mock_resp, mock_album, mock_songs"
, [
    (
        ["Four_Calendar_Cafe-Cocteau Twins", "LASFTFM", "n", "y", "n"],
        [],
        {"mock":"bad_lasfm_resp"},
        {"album" : "Four Calendar Cafe", "artist": "Cocteau Twins"}, #correct album would be Four-Calendar Cafe
        []
    ),
    (
        ["Goo-Sonic_Youth", "LASTFM", "y", "", ""],
        ["song1", "song2"],
        {"mock" : "lastfm_resp"},
        {"album": "Goo", "artist": "Sonic Youth"},
        ["song1", "song2"]
    ),
    (
        ["Daydream_Nation-Sonic_Youth", "DISCOGS", "n", "y", "y"],
        ["song1", "song2"],
        {"mock" : "discogs_resp"},
        {"album": "Daydream Nation", "artist": "Sonic Youth"},
        ["song1", "song2"]
    )
])
@patch("src.handle_metadata.get_album_data_from_discogs")
@patch("src.handle_metadata.fetcher.get_album_discogs")
@patch("src.handle_metadata.get_album_data_from_lastfm")
@patch("src.handle_metadata.check_album")
@patch("src.handle_metadata.fetcher.get_album_lastfm")
@patch("builtins.input")
def test_get_album_from_repo(
    mock_input,
    mock_get_album_lastfm,
    mock_check_album,
    mock_get_album_data_from_lastfm,
    mock_get_album_discogs,
    mock_get_album_data_from_discogs,
    inputs,
    expected_result,
    mock_resp,
    mock_album,
    mock_songs
):
    
    query = inputs[0].split("-")
    artist_str = query[-1].replace(" ", "+").replace("_","+")
    album_str = query[0].replace(" ", "+").replace("_", "+")

    mock_input.side_effect = inputs[2:]
    
    mock_check_album.return_value = mock_album

    response_obj = {}
    if inputs[1] == "LASTFM":
        mock_lastfm_response = Mock()
        mock_lastfm_response.json.return_value = mock_resp
        mock_get_album_lastfm.return_value = mock_lastfm_response

        mock_get_album_data_from_lastfm.return_value = mock_songs

        response_obj = mock_lastfm_response

    else:
        mock_discogs_response = Mock()
        mock_discogs_response.json.return_value = mock_resp
        mock_get_album_discogs.return_value = mock_discogs_response
        
        mock_get_album_data_from_discogs.return_value = mock_songs

        response_obj = mock_discogs_response

    result = handle_metadata.get_album_from_repo(inputs[0], False)

    assert result == expected_result
    
    if inputs[1] == "LASTFM" and inputs[2] == "y":
        #auto search lastfm success
        expected_artist_query = artist_str.replace(" ", "+")
        expected_album_query = album_str.replace(" ", "+")
        mock_get_album_lastfm.assert_called_once_with(expected_artist_query, expected_album_query, False)
            
        mock_get_album_data_from_lastfm.assert_called_once_with(
            mock_check_album.return_value, response_obj, False)

        #verify discogs not called
        mock_get_album_discogs.assert_not_called()
        mock_get_album_data_from_discogs.assert_not_called()

    elif inputs[1] == "DISCOGS" and inputs[2] == "n" and inputs[3] == "y" and inputs[4] == "y":
        #last fm failed , discogs success
        album_query = inputs[0].replace("-", " by ").replace("_", " ")
        mock_get_album_discogs.assert_called_once_with(album_query)

        mock_check_album.assert_called_with(
            response_obj, inputs[1])

        mock_get_album_data_from_discogs.assert_called_once_with(mock_check_album.return_value, response_obj, False)

        #verify not lastfm
        mock_get_album_data_from_lastfm.assert_not_called()

    elif inputs[1] == "LASTFM" and inputs[2] == "n" and inputs[3] == "y" and inputs[4] == "n":
        #rejected by user
        mock_get_album_lastfm.assert_called_once()
        mock_check_album.assert_called_once()
        mock_get_album_data_from_lastfm.assert_not_called()
        mock_get_album_discogs.assert_not_called()
        mock_get_album_data_from_discogs.assert_not_called()

@pytest.mark.parametrize("expected, path, file, bit_rate, is_saved",[
    (
        True,
        "../album/",
        "file1.wav",
        192,
        True
    ),
    (
        True,
        "../album",
        "file1.mp3",
        192,
        False
    )
])
@patch("src.handle_metadata.subprocess.run")
@patch("src.handle_metadata.prompts.clean_up")
@patch("src.handle_metadata.prompts.save_metadata_ffmpeg")
@patch("src.handle_metadata.prompts.convert_to_mp3_with_selected_bitrate")
@patch("src.handle_metadata.prompts.copy_to_temp")
@patch('src.handle_metadata.Song')
def test_modify_metadata_ffmpeg(
    mock_song_class,
    mock_copy,
    mock_convert_to_mp3,
    mock_ffmpeg_cmd,
    mock_clean_up,
    mock_subprocess,
    expected,
    path,
    file,
    bit_rate,
    is_saved):
    
    mock_song = Mock()
    mock_song.title = "song_title"
    mock_song.track_num = 1
    mock_song_class.return_value = mock_song

    mock_copy.return_value = "cp source dest"
    mock_convert_to_mp3.return_value = "ffmpeg convert cmd"
    mock_ffmpeg_cmd.return_value = "ffmpeg metadata cmd"
    mock_clean_up.return_value = "rm cmd"

    #determine file type
    is_mp3 = file.endswith(".mp3")

    result = handle_metadata.modify_metadata_ffmpeg(path, file, mock_song, bit_rate, is_saved, False)
    assert result == expected

    assert mock_copy.call_count == 1
    source_arg , dest_arg = mock_copy.call_args[0]

    expected_source = os.path.join(os.path.dirname(path), file ) if " " not in file else os.path.join(os.path.dirname(path), f"'{file}'")
    assert source_arg == expected_source
    clean = "".join(e for e in mock_song.title if e.isalnum())
    assert clean in dest_arg
    assert dest_arg.endswith(f".{file.split('.')[-1]}")

    mock_subprocess.assert_any_call(
        [mock_copy.return_value], shell=True, check=False
    )

    #if not mp3 then convert
    if not is_mp3:
        assert mock_convert_to_mp3.call_count == 1

        mock_subprocess.assert_any_call([mock_convert_to_mp3.return_value], shell=True, check=False)
    else:
        assert mock_convert_to_mp3.call_count == 0

    assert mock_ffmpeg_cmd.call_count == 1
    ffmpeg_args = mock_ffmpeg_cmd.call_args[0]
    assert ffmpeg_args[0] == is_saved

    mock_subprocess.assert_any_call([mock_ffmpeg_cmd.return_value], shell=True, check=False)

    assert mock_clean_up.call_count == 1
    cleanup_arg = mock_clean_up.call_args[0][0]
    mock_subprocess.assert_any_call(
        [f'rm {cleanup_arg}'], shell=True, check=False
    )

@pytest.mark.parametrize("scenario", [
    {
        "path": "some/path/album_name-artist_name",
        "dir_list": ["track1.wav", "track2.wav"],
        "sorted_list": ["track1.wav", "track2.wav"],
        "songs_from_repo": [],  # Empty, triggers manual search
        "manual_songs": [Mock(title="manual1", track_num=1, cover="cover1.jpg"),
                        Mock(title="manual2", track_num=2, cover="cover2.jpg")],
        "album_name": "album_name-artist_name",
        "bit_rate": 192,
        "successful_save": True,
        "success": True,
        "expected": True
    },
    {
        "path": "some/path/album_name-artist_name",
        "dir_list": ["track1.wav", "track2.wav"],
        "sorted_list": ["track1.wav", "track2.wav"],
        "songs_from_repo": [Mock(title="song1", track_num=1, cover="cover1.jpg")],
        "manual_songs": [],
        "album_name": "album_name-artist_name",
        "bit_rate": 192,
        "successful_save": False,  # Album image fails
        "success": False,  # Conversion fails
        "expected": False  # Should return False because success is False
    }
])
@patch("src.handle_metadata.util.remove_wavs")
@patch("src.handle_metadata.modify_metadata_ffmpeg")
@patch("src.handle_metadata.get_album_image")
@patch("src.handle_metadata.prompts.get_bit_rate")
@patch("src.handle_metadata.manual_search")
@patch("src.handle_metadata.get_album_from_repo")
@patch("src.handle_metadata.util.sort_tracks")
@patch("src.handle_metadata.subprocess.call")
@patch("src.handle_metadata.os")
@patch("builtins.input")
def test_save_album_metadata_scenarios(
    mock_input,
    mock_os,
    mock_subprocess_call,
    mock_sort,
    mock_repo,
    mock_manual,
    mock_bit_rate,
    mock_album_image,
    mock_modify,
    mock_clean_files,
    scenario):
    
    # Setup OS mocks
    mock_os.path.exists.return_value = True
    mock_os.path.isdir.return_value = True
    mock_os.path.join.side_effect = lambda *args: "/".join(args)
    mock_os.path.split.return_value = ("some/path", scenario["album_name"])
    mock_os.listdir.return_value = scenario["dir_list"]
    mock_os.mkdir.return_value = None
    
    # Setup input mock
    mock_input.return_value = scenario["path"]
    
    # Setup sort_tracks
    mock_sort.return_value = None
    
    # Setup repo and manual search
    mock_repo.return_value = scenario["songs_from_repo"]
    mock_manual.return_value = scenario["manual_songs"]
    
    # Setup bit rate
    mock_bit_rate.return_value = scenario["bit_rate"]
    
    # Setup album image - returns True for first call, False for others
    mock_album_image.side_effect = lambda *args: scenario["successful_save"] if mock_album_image.call_count == 0 else False
    
    # Setup modify_metadata_ffmpeg
    mock_modify.return_value = scenario["success"]
    
    # Call function
    result = handle_metadata.save_album_metadata(False)
    
    # Assert result
    assert result == scenario["expected"]