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
            {"album": "Goo", "artist": "Sonic Youth", "release_date" : datetime.datetime(1990, 6, 26, 0, 0), "source": "LASTFM"}
        ),
        (
            "DISCOGS",
            discogs_test,
            {"album": "Daydream Nation", "artist": "Sonic Youth", "release_date" : datetime.datetime(1988, 1, 1, 0, 0), "source": "DISCOGS"}
        )
    ])
def test_check_album(platform, test_album, expected):
    '''
        Test check_album().
    '''
    assert expected == handle_metadata.check_album(test_album, platform)

@pytest.mark.parametrize("album, resp, expected_count, expected_attrs",[
    (
        # album
        {'album': "Daydream Nation", 'artist': "Sonic Youth", 'release_date': datetime.datetime(1988, 1, 1, 0, 0), 'source': "DISCOGS"},
        
        # resp
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
        
        # expected method calls for each track (as a list of expected call sequences)
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
        # album
        {"album": "Goo", "artist": "Sonic Youth", "release_date": datetime.datetime(1990, 1, 1, 0, 0), 'source': "DISCOGS"},
        
        # resp
        {
            'images': [{'uri': 'https://example.com/goo_cover.jpg'}],
            'styles': [],
            'genres': ['Alternative Rock'],
            'tracklist': [
                {'title': 'Dirty Boots'},
                {'title': 'Tunic (Song for Karen)'}
            ],
            'year': 1990
        },
        
        # number of tracks
        2,
        
        # expected method calls for each track
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
        {"album": "Daydream Nation", "artist": "Sonic Youth", "release_date" : datetime.datetime(1988, 1, 1, 0, 0), 'source': "DISCOGS"},

        #dummy response
        discogs_test,
        
        #tracks
        14,
        
        # dummy object
        {
            'artist': 'Sonic Youth',
            'album_artist': 'Sonic Youth',
            'album': 'Daydream Nation',
            'cd': 1,
            'genre': 'Alternative Rock',
            'year': 1988,
            'cover': 'https://i.discogs.com/WFA7Kod1I11LlmFF9Y8pU-uwf1yS58cutjotHKDdAKs/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEzNTI1/NzItMTU0MTk3NzU1/Mi00OTYyLmpwZWc.jpeg'
        }
    ),
    
    #lastfm test cases
    (
        #album
        {"album": "Goo", "artist": "Sonic Youth", "release_date" : datetime.datetime(1990, 6, 26, 0, 0), "source": "LASTFM"},
        
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
        {"album": "Daydream Nation", "artist": "Sonic Youth", "release_date" : datetime.datetime(1988, 1, 1, 0, 0), "source": "LASTFM"},
        
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
        {"album": "Goo", "artist": "Sonic Youth", "release_date" : datetime.datetime(1992, 6, 26, 0, 0), "source": "LASTFM"},

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
@patch('src.handle_metadata.SongBuilder')
def test_get_album_data_from_source(mock_songbuilder_class, album, resp, expected_count, expected_attrs):
    '''
        Test get_album_data_from_discogs with mocked Song class.
    '''
    mock_instance = [Mock() for _ in range(expected_count)]
    mock_songbuilder_class.side_effect = mock_instance

    for i in mock_instance:
        i.title.return_value = i
        i.artist.return_value = i
        i.album.return_value = i
        i.album_artist.return_value = i
        i.genre.return_value = i
        i.year.return_value = i
        i.track_num.return_value = i
        i.cover.return_value = i

    mock_songs = [Mock() for _ in range(expected_count)]
    for i, j in zip(mock_instance, mock_songs):
        i.build.return_value = j

    result = handle_metadata.get_album_data_from_source(album, resp)

    assert mock_songbuilder_class.call_count == expected_count
    mock_songbuilder_class.assert_has_calls([call()] * expected_count)

    if album["source"] == "DISCOGS":
        tracks = resp['tracklist']
        track_str = 'title'
       
    else:
        tracks = resp['album']['tracks']['track']
        track_str = 'name'

    expected_calls = []
    for i , (m, track) in enumerate(zip(mock_instance, tracks)):
        expected_attrs = expected_attrs.copy()
        expected_attrs[track_str] = track[track_str]
        expected_attrs['track_num'] = i + 1
        expected_calls.append(call(**expected_attrs))

        m.build.asset_called_once()

    assert result == mock_songs
    assert len(result) == expected_count

# @pytest.mark.parametrize("inputs, expected_result, mock_resp, mock_album, mock_songs", [
#     (
#         # Test case 1: User says yes to manual search and yes to correct album
#         ["y", "Sonic Youth", "Daydream Nation", "y"],
#         ["song1", "song2"],  # Expected return value (list of Song objects)
#         {"mock": "lastfm_response"},  # Mock response from get_album_lastfm
#         {"album": "Daydream Nation", "artist": "Sonic Youth"},  # Mock album from check_album
#         ["song1", "song2"]  # Mock songs from get_album_data_from_lastfm
#     ),
#     (
#         # Test case 2: User says yes to manual search but no to correct album
#         ["y", "Sonic Youth", "Goo", "n"],
#         [],  # Expected return value (empty list)
#         {"mock": "lastfm_response"},
#         {"album": "Goo", "artist": "Sonic Youth"},
#         None  # Not used because get_album_data_from_lastfm won't be called
#     ),
#     (
#         # Test case 3: User says no to manual search
#         ["n"],
#         [],  # Expected return value (empty list)
#         None,  # Not used
#         None,  # Not used
#         None   # Not used
#     ),
#     (
#         # Test case 4: User enters invalid input
#         ["  ", "Sonic Youth", "Daydream Nation", "y"],
#         [],
#         {"mock": "lastfm_response"},
#         {"album": "Daydream Nation", "artist": "Sonic Youth"},
#         ["song1", "song2"]
#     )
# ])
# @patch('src.handle_metadata.prompts.wow_niche')
# @patch('src.handle_metadata.get_album_data_from_source')
# @patch('src.handle_metadata.check_album')
# @patch('src.handle_metadata.fetcher.get_album_lastfm')
# @patch('builtins.input')
# def test_manual_search_gets_track_list():
    #TODO: re-write tests.

# @pytest.mark.parametrize("expected, path, file, bit_rate, is_saved",[
#     (
#         True,
#         "../album/",
#         "file1.wav",
#         192,
#         True
#     ),
#     (
#         True,
#         "../album",
#         "file1.mp3",
#         192,
#         False
#     )
# ])
# @patch("src.handle_metadata.subprocess.run")
# @patch("src.handle_metadata.prompts.save_metadata_ffmpeg")
# @patch("src.handle_metadata.prompts.convert_to_mp3_with_selected_bitrate")
# @patch("src.handle_metadata.prompts.copy_to_temp")
# @patch('src.handle_metadata.Song')
# def test_modify_metadata_ffmpeg():
    # TODO: re-write tests.

# @pytest.mark.parametrize("scenario", [
#     {
#         "inputs": ["y", ""], #correct and try again inputs
#         "album_query": "album_name-artist_name",
#         "get_album_from_lastfm": Mock(json_response={"mock": "response"}, is_success=True, result_list = []),
#         "check_album" : {"mock": "album"},
#         "valid_discogs_flow": [], # doesn't occurr
#         "get_album_data_from_source": [Mock(title="song1", album="album1", artist="artist1"), Mock(title="song2", album="album2", artist="artist2")]
#     },
#     {
#         "inputs": ["n", "y"], #user rejects lastfm response and tries again
#         "album_query": "album_name-artist_name",
#         "get_album_from_lastfm" : Mock(json_response={"mock": "response"}, is_success=True, result_list = []),
#         "check_album": {"mock" : "album"},
#         "valid_discogs_flow" : [Mock(title="song1", album="album1", artist="artist1"), Mock(title="song2", album="album2", artist="artist2")],
#         "gel_album_data_from_source" : [] # not needed
#     },

# ])
# @patch('src.handle_metadata.valid_discogs_flow')
# @patch('src.handle_metadata.get_album_data_from_source')
# @patch('src.handle_metadata.check_album')
# @patch('src.fetcher.get_album_lastfm')
# @patch("builtins.input")
# def test_get_response_from_repo():
    # TODO: rewrite tests.

# @pytest.mark.parametrize("scenario", [
#     {
#         "path": "some/path/album_name-artist_name",
#         "dir_list": ["track1.wav", "track2.wav"],
#         "sorted_list": ["track1.wav", "track2.wav"],
#         "response_from_repo": Mock(response_body={"mock":"response"}, is_succcess=False, result_list = []),  # Empty, triggers manual search
#         "manual_songs": [Mock(title="manual1", track_num=1, cover="cover1.jpg"),
#                         Mock(title="manual2", track_num=2, cover="cover2.jpg")],
#         "album_name": "album_name-artist_name",
#         "bit_rate": 192,
#         "successful_save": True,
#         "success": True,
#         "expected": True
#     },
#     {
#         "path": "some/path/album_name-artist_name",
#         "dir_list": ["track1.wav", "track2.wav"],
#         "sorted_list": ["track1.wav", "track2.wav"],
#         "response_from_repo": Mock(response_body={"mock":"album"}, is_succcess=True, result_list = [Mock(title="song1", album="album1", artist="artist1"), Mock(title="song2", album="album2", artist="artist2")]),
#         "manual_songs": [],
#         "album_name": "album_name-artist_name",
#         "bit_rate": 192,
#         "successful_save": False,  # Album image fails
#         "success": False,  # Conversion fails
#         "expected": False  # Should return False because success is False
#     }
# ])
# @patch("src.handle_metadata.util.remove_wavs")
# @patch("src.handle_metadata.modify_metadata_ffmpeg")
# @patch("src.handle_metadata.get_album_image")
# @patch("src.handle_metadata.prompts.get_bit_rate")
# @patch("src.handle_metadata.manual_search")
# @patch("src.handle_metadata.get_response_from_repo")
# @patch("src.handle_metadata.util.sort_tracks")
# @patch("src.handle_metadata.subprocess.call")
# @patch("src.handle_metadata.os")
# @patch("builtins.input")
# def test_save_album_metadata_scenarios():
    # TODO: re-write test