# Example image batch manifest (from a Salah video): (out_rel, refs_rel, prompt). Paths relative to the video folder.
MS, MT, MA, MTH = ("03_character/master_SAL.jpg", "03_character/master_TEEN_SAL.jpg",
                   "03_character/master_ABBAS.jpg", "03_character/master_THIEF.jpg")
P = lambda n: f"04_backgrounds/poses/{n}.jpg"
S = lambda n: f"04_backgrounds/shots/{n}.jpg"
PL = lambda n: f"04_backgrounds/plates/{n}.jpg"

Q = ("Bright high-key light, vivid saturated colours. Sharp deep focus, high clarity, punchy contrast, warm skin, "
     "natural soft contact shadows. Photoreal editorial photograph, vertical 9:16. No readable text, letters, logos or numbers anywhere except a kit number.")
FULL = "full body filling most of the frame height, face and head in the upper half of the frame"
SAL = "Mohamed Salah (the man in the reference image: DARK VOLUMINOUS CURLY HAIR, FULL DARK TRIMMED BEARD, warm brown skin, slim athletic build)"
LIV = "a Liverpool-style look-alike home kit (BRIGHT RED shirt, red shorts, red socks, white number 11, small round crest-like badge, NO sponsor text)"
TEEN = "young Mohamed Salah aged about 15 (the boy in the reference image: SHORT DARK CURLY HAIR, NO BEARD, boyish face, skinny build)"
YKIT = "the yellow look-alike youth kit with thin black vertical stripes, black shorts, yellow socks"
UNI = "a plain school uniform (white short-sleeve shirt, grey trousers) with a dark kit bag"
ABB = "the invented club president from the reference image (NEAT GREY HAIR, THICK GREY MOUSTACHE, navy suit, gold watch)"
THF = "the comic burglar from the reference image (stubble, black-and-white striped jumper, black beanie, sack)"
SAME = "Same person, same outfit, same location, same light and exactly the same camera position and size in frame as the first reference image."

J = []
def add(out, refs, prompt): J.append((out, refs, prompt))

# ---- Hook
add(P("H01_pr1"), [MS], f"{SAL}, wearing {LIV}, medium shot from the knees up on a sunny pitch-side touchline with a blurred stadium crowd. Caught MID-ACTION: BOTH HANDS HIDDEN BEHIND HIS BACK, leaning in with a CHEEKY KNOWING GRIN, eyebrows raised. {Q}")
add(P("H01_pr2"), [P("H01_pr1"), MS], f"{SAME} Only change: he now HOLDS A SHINY GOLDEN FOOTBALL BOOT UP towards the camera with both hands, BIG PROUD TOOTHY GRIN. {Q}")
add(S("H02"), [MS, P("H01_pr2")], f"{SAL}, wearing {LIV}, standing {FULL}, on a sunny pitch-side touchline, HOLDING A SHINY GOLDEN FOOTBALL BOOT ALOFT above his head with one hand, other fist pumped, HUGE GRIN. Eye-level, frontal 3/4. {Q}")
add(S("H03"), [MS], f"CLOSE-UP of {SAL}, wearing {LIV}, head and shoulders filling the frame, holding a SHINY GOLDEN FOOTBALL BOOT right next to his cheek, BIG CHEEKY GRIN straight into the lens, sunny stadium softly blurred behind. {Q}")
# ---- #10
add(S("A01"), [MT], f"{TEEN}, wearing {YKIT}, {FULL}, on a dusty sunlit youth football pitch with patchy grass, palm trees and low sandy buildings behind. Caught MID-ACTION in a LOW DEFENDING CROUCH, knees bent, ARMS OUT WIDE, FIERCE CONCENTRATED FACE, tongue poking out. Eye-level. Exactly 1 person. {Q}")
add(P("A02_dr1"), [MT], f"{TEEN}, wearing {YKIT}, {FULL}, side-on, DRIBBLING a white football up the wing of a dusty sunlit youth pitch, moving towards the RIGHT side of the frame, LEFT FOOT TOUCHING THE BALL, arms pumping, DETERMINED FACE. Exactly 1 person. {Q}")
add(P("A02_dr2"), [P("A02_dr1"), MT], f"{SAME} Only change: mid-stride, now his RIGHT FOOT TOUCHES THE BALL, left leg trailing behind. {Q}")
add(P("A03_k1"), [MT], f"Wide low angle on a dusty sunlit youth pitch facing a rusty goal. On the LEFT, {TEEN}, wearing {YKIT}, full body, side-on, WIND-UP: plant foot down, KICKING LEG SWUNG FAR BACK, arms out. In the goal on the RIGHT, a goalkeeper boy in a grey jersey crouched ready. NO BALL anywhere in the image. Exactly 2 people. {Q}")
add(P("A03_k2"), [P("A03_k1"), MT], f"{SAME} Only change: CONTACT moment, kicking foot swung forward beside the plant foot, body leaning. Goalkeeper unchanged. NO BALL anywhere in the image. {Q}")
add(P("A03_k3"), [P("A03_k2"), MT], f"{SAME} Only change: FOLLOW-THROUGH, kicking leg HIGH in the air, face WINCING; the goalkeeper is BENT OVER LAUGHING, pointing. NO BALL anywhere in the image. {Q}")
add(P("A04_a"), [MT], f"Medium shot on a sunny pitch-side bench. {TEEN}, wearing {YKIT}, seated, head down, LIP TREMBLING, about to cry. Beside him on the RIGHT, a youth coach in his 40s in a grey tracksuit with a whistle round his neck, looking at him kindly. Exactly 2 people. {Q}")
add(P("A04_b"), [P("A04_a"), MT], f"{SAME} Only change: the boy is now CRYING comically, BIG TEARS, face scrunched, fists at his eyes; the coach PATS HIS HEAD sympathetically. {Q}")
# ---- #9
add(S("B01"), [MT], f"Wide shot of an OVERLOADED old white minibus driving along a straight desert road in bright morning sun, luggage, crates and a bicycle piled HIGH on the roof, passengers squeezed inside. {TEEN}, wearing {UNI}, has his HEAD AND ONE ARM OUT OF THE SIDE WINDOW, hair blown by the wind, cheeky grin. Sand dunes and blue sky. {Q}")
add(P("B02_a"), [MT], f"Medium shot inside a crowded old minibus, bright sunlight through the windows. {TEEN}, wearing {UNI}, SQUASHED between a large smiling aunt with shopping bags on the LEFT and a WHITE GOAT on the RIGHT standing on the seat. His face is pressed and uncomfortable. {Q}")
add(P("B02_b"), [P("B02_a"), MT], f"{SAME} Only change: the GOAT LICKS HIS EAR with its tongue out; the boy gives a DISGUSTED SIDE-EYE towards the goat, mouth pulled sideways. {Q}")
for i, place in enumerate(["a green town bus in a busy Egyptian town street", "a rusty old bus waiting at a dusty roadside stop",
                           "a minibus crawling past a colourful market", "a big city bus stuck in heavy Cairo traffic"], 1):
    add(P(f"B03_{i}"), [MT], f"Wide shot of {place}, bright daylight. {TEEN}, wearing {UNI}, at an open side window in the centre of the frame, chin on his kit bag, TIRED BORED FACE. {Q}")
add(S("B04"), [MT], f"Medium shot inside a bus in bright morning light. {TEEN}, wearing {UNI}, FAST ASLEEP slumped on his kit bag against the window, MOUTH WIDE OPEN, a little drool, hair squashed. Exactly 1 person in focus. {Q}")
# ---- #8
add(S("C01"), [MA, MT], f"Wide shot of a bright sunlit club office with wood panelling and trophy shelves (plain pennants with no crests or text). On the LEFT, {ABB}, LOUNGING in a HUGE oversized leather chair behind a big desk, fingers steepled, unimpressed. On the RIGHT, {TEEN}, wearing a red youth tracksuit, standing NERVOUSLY, clutching a football to his chest, gulping. Exactly 2 people. {Q}")
add(P("C02_n0"), [MA], f"Medium shot of {ABB} in the bright club office with trophy shelves (plain pennants, no crests), from the waist up, looking at camera, UNIMPRESSED frown, arms folded. Exactly 1 person. {Q}")
add(P("C02_nl"), [P("C02_n0"), MA], f"{SAME} Only change: his HEAD IS TURNED to the LEFT side of the frame (shaking his head no), eyes closed, lips pursed. {Q}")
add(P("C02_nr"), [P("C02_n0"), MA], f"{SAME} Only change: his HEAD IS TURNED to the RIGHT side of the frame (shaking his head no), eyes closed, lips pursed. {Q}")
add(P("C03_pr1"), [MS, MA], f"Medium two-shot at a sunny stadium entrance gate with red brick and railings. On the LEFT: {SAL}, now in a smart light-grey suit and open white shirt, one HAND HIDDEN BEHIND HIS BACK, warm cheeky smile. On the RIGHT: {ABB}, looking CURIOUS and suspicious. Both from the knees up, same size. Exactly 2 people. {Q}")
add(P("C03_pr2"), [P("C03_pr1"), MS, MA], f"{SAME} Only change: Salah now HOLDS OUT a shiny GOLDEN VIP TICKET (blank, no text) towards the older man with a big generous grin; the older man stares at it. {Q}")
add(P("C04_a"), [MA], f"CLOSE-UP of {ABB}, head and shoulders filling the frame, NEUTRAL face, at a sunny stadium entrance gate softly blurred behind. {Q}")
add(P("C04_b"), [P("C04_a"), MA], f"Exactly the same close-up as the first reference image: same framing, head size, light and background. Only change: JAW DROPPED wide open, EYES BULGING, eyebrows shot up, totally SHOCKED. {Q}")
# ---- #7
add(S("D01"), [MA, MS], f"Full two-shot in front of a luxury white villa with a pool and palm trees, sunny. On the LEFT: {ABB}, proudly PRESENTING a GIANT GOLDEN KEY as big as his arm with both hands. On the RIGHT: {SAL}, wearing a red Egypt-style look-alike tracksuit (no text), full body, SURPRISED, eyebrows up, hand on his chest. Both full body, same size. Exactly 2 people. {Q}")
add(P("D02_n0"), [MS], f"Medium shot of {SAL}, wearing a red Egypt-style look-alike tracksuit (no text), waist up, in front of a sunny luxury white villa with palm trees, POLITE WARM SMILE, looking at camera. Exactly 1 person. {Q}")
add(P("D02_nl"), [P("D02_n0"), MS], f"{SAME} Only change: HEAD TURNED to the side (shaking no), ONE HAND RAISED palm out, politely declining, still smiling. {Q}")
add(P("D03_p0"), [P("D02_n0"), MS], f"{SAME} Only change: arms relaxed down, looking slightly to the RIGHT side of the frame, gentle smile. {Q}")
add(P("D03_p1"), [P("D03_p0"), MS], f"{SAME} Only change: his ARM FULLY EXTENDED, POINTING off towards the RIGHT side of the frame, WARM BIG SMILE. {Q}")
add(S("D04"), [], f"Wide shot of a bright sunny Egyptian village square with sandy houses and palm trees: a crowd of happy village kids JUMPING and CHEERING with arms up around a shiny brand-new white ambulance (no text or logos on it). {Q}")
# ---- #6
add(P("E01_wr1"), [MS], f"Medium shot of {SAL}, wearing a cosy beige cardigan over a white T-shirt, SEATED at a small table in a cosy bright sunlit living room, PEN ON A SMALL WHITE CARD, writing carefully, tongue out in concentration; the card has only soft illegible squiggles. Exactly 1 person. {Q}")
add(P("E01_wr2"), [P("E01_wr1"), MS], f"{SAME} Only change: the pen has moved to the right end of the card, he looks up with a PROUD SOFT SMILE. Card lettering still illegible squiggles. {Q}")
add(S("E02"), [], f"Wide shot of a bright, warmly lit British bingo hall: rows of tables with cheerful grannies holding colourful dabbers over bingo cards (cards with tiny illegible numbers), concentrating hard, pastel cardigans, patterned carpet. {Q}")
add(P("E03_a"), [], f"Medium shot in a bright British bingo hall: one cheerful grey-haired granny in a lilac cardigan seated at a table, colourful DABBER POISED over her card, eyes narrowed with intense focus; other players softly blurred. {Q}")
add(P("E03_b"), [P("E03_a")], f"{SAME} Only change: she JUMPS UP OUT OF HER SEAT, BOTH ARMS RAISED, mouth WIDE OPEN SHOUTING with joy, dabber in her fist. {Q}")
add(P("E04_s0"), [MS], f"CLOSE-UP of {SAL}, wearing a cosy beige cardigan, head and shoulders filling the frame, NEUTRAL calm face looking into the lens, cosy bright living room softly blurred behind. {Q}")
add(P("E04_s1"), [P("E04_s0"), MS], f"Exactly the same close-up as the first reference image: same framing, head size, light and background. Only change: SLOW SIDE-EYE to the side, ONE EYEBROW RAISED, lips pressed, deadpan. {Q}")
# ---- #5
add(P("F01_a"), [], f"Wide shot of a sunny resort plaza with palm trees and a blue sky: a tall statue on a plinth FULLY COVERED by a red cloth, a small crowd of smiling tourists and officials waiting in front, phones raised. {Q}")
add(P("F01_b"), [P("F01_a")], f"{SAME} Only change: the cloth has dropped to the ground revealing a bronze-coloured footballer statue with a COMICALLY GIANT OVERSIZED HEAD on a small body, curly hair and beard; the crowd GASPS, hands over mouths. {Q}")
add(P("F02_t1"), [MS], f"Medium shot of {SAL}, wearing a crisp white polo shirt, waist up, in a sunny resort plaza with palm trees, LOOKING AWAY to the side, relaxed and smiling. Exactly 1 person. {Q}")
add(P("F02_t3"), [P("F02_t1"), MS], f"{SAME} Only change: he has snapped round to FACE THE CAMERA, totally SHOCKED, mouth wide open, eyes wide (a double-take). {Q}")
# ---- #4
add(P("G01_sn1"), [MTH], f"{THF}, {FULL}, side-on, TIPTOEING towards the RIGHT side of the frame along a bright sunny Egyptian village street with sandy houses, wooden doors and potted plants, SACK over his shoulder, knees bent high, FINGER ON HIS LIPS, eyes darting. Exactly 1 person. {Q}")
add(P("G01_sn2"), [P("G01_sn1"), MTH], f"{SAME} Only change: next tiptoe step, his OTHER FOOT is now forward and lifted. {Q}")
add(P("G02_a"), [MS, MTH], f"Medium two-shot on a bright sunny Egyptian village street. On the LEFT: {SAL}, wearing a casual dark tracksuit, kindly REACHING OUT a plain white envelope. On the RIGHT: {THF}, SURPRISED, hands half raised, mouth open. Both waist up, same size. Exactly 2 people. {Q}")
add(P("G02_b"), [P("G02_a"), MS, MTH], f"{SAME} Only change: the burglar now HOLDS THE ENVELOPE in both hands, STUNNED, eyes welling up; Salah smiles warmly. {Q}")
add(P("G03_a"), [P("G02_b"), MS, MTH], f"{SAME} Only change: the burglar now wears a YELLOW HARD HAT instead of the beanie, ARMS OPENING wide, EYES WELLING with tears of joy, chin wobbling. {Q}")
add(P("G03_b"), [P("G03_a"), MS, MTH], f"{SAME} Only change: the burglar in the yellow hard hat HUGS SALAH TIGHTLY, CRYING WITH JOY; Salah LAUGHS, patting his back. {Q}")
# ---- #3
add(P("J01_a"), [], f"Wide shot of a sunny football stadium stand packed with happy fans in red, red scarves held DOWN at chest height, mouths open singing. {Q}")
add(P("J01_b"), [P("J01_a")], f"{SAME} Only change: all the fans now hold their RED SCARVES RAISED HIGH above their heads, stretched out, singing loudly. {Q}")
add(S("J02"), [MS], f"{SAL}, wearing {LIV}, {FULL}, RUNNING towards the camera on a sunny stadium pitch with a red-scarf crowd behind, ARMS SPREAD WIDE like wings, JOYFUL OPEN-MOUTH SHOUT. Exactly 1 person in focus. {Q}")
add(P("J03_a"), [MS], f"{SAL}, wearing {LIV}, {FULL}, on a sunny stadium pitch in front of a red-scarf crowd, RUNNING with ARMS WIDE, big joyful smile. Exactly 1 person in focus. {Q}")
add(P("J03_b"), [P("J03_a"), MS], f"{SAME} Only change: he is now KNEELING on the grass, BOTH ARMS RAISED to the sky, celebrating, eyes closed, big smile. {Q}")
# ---- #2
add(P("K01_p0"), [], f"Medium shot in a bright university lecture hall: a cheerful professor in her 50s with glasses and a blazer standing beside a large screen showing a simple line chart with a line FALLING steeply down (no numbers, no text). {Q}")
add(P("K01_p1"), [P("K01_p0")], f"{SAME} Only change: she now has her ARM FULLY EXTENDED, POINTING at the falling line, eyebrows raised, delighted. {Q}")
add(P("K02_n0"), [MS], f"Medium shot of {SAL}, wearing a plain grey hoodie, seated in the front row of a bright lecture hall, waist up, head level, PROUD WARM SMILE. Exactly 1 person in focus. {Q}")
add(P("K02_n1"), [P("K02_n0"), MS], f"{SAME} Only change: his HEAD TILTED DOWN in a proud nod, eyes closed, smiling. {Q}")
add(P("K03_a"), [], f"Full two-shot on a sunny terraced street in Liverpool with red-brick houses: two friendly neighbours, an older white man in a flat cap on the LEFT and a young man in a red hoodie on the RIGHT, both full body, HANDS RAISED high about to HIGH-FIVE, big grins. Exactly 2 people. {Q}")
add(P("K03_b"), [P("K03_a")], f"{SAME} Only change: their PALMS SLAP TOGETHER in a high-five, both LAUGHING. {Q}")
# ---- #1
add(S("L01"), [], f"Wide shot of a bright, sunlit polling hall with simple wooden voting booths: cheerful voters GRINNING mischievously, scribbling on paper ballots (ballots with only illegible squiggles), no flags, no logos, no politicians. {Q}")
add(P("L02_a"), [], f"Medium shot in a bright polling hall: a clear plastic ballot box on a table, FULL TO THE TOP with folded white paper ballots (no text). {Q}")
add(P("L02_b"), [P("L02_a")], f"{SAME} Only change: the ballots are BURSTING OUT of the top of the box, flying up into the air like confetti. {Q}")
add(P("L03_g1"), [MS], f"CLOSE-UP of {SAL}, wearing a sharp navy suit and white shirt, head and shoulders filling the frame, NEUTRAL calm face looking straight into the lens, plain bright warm-cream backdrop. {Q}")
add(P("L03_g2"), [P("L03_g1"), MS], f"Exactly the same close-up as the first reference image: same framing, head size, light and background. Only change: a CHEEKY WINK with one eye, confident HALF-SMILE. {Q}")
# ---- Prop
add("04_backgrounds/props/BALL.jpg", [], "Photoreal product photo of a single classic white football with black pentagon panels, slightly worn, centred, filling about 70% of the frame, lit by bright daylight from the left, on a perfectly plain flat solid mid-grey background. Sharp focus, no shadow on the background, no text, no logos.")
# ---- Plates (after their source stills)
PLATE = "Same place, same light and exactly the same camera position as the reference image, but with NO PEOPLE and NO ANIMALS at all: everyone is completely removed, leaving only the empty set. Clean background plate, photoreal, vertical 9:16, sharp deep focus. No text."
for name, ref, extra in [("P_PITCH", S("H02"), "Empty sunny pitch-side touchline and stands."),
                         ("P_YOUTH", S("A01"), "Empty dusty youth pitch."),
                         ("P_YOUTH_GOAL", P("A03_k2"), "Empty youth pitch and goal; the goalkeeper may stay in the goal, the kicker is removed."),
                         ("P_DESERT", S("B01"), "Empty straight desert road, NO minibus or vehicles."),
                         ("P_OFFICE", S("C01"), "Empty bright office with the huge leather chair."),
                         ("P_VILLA", S("D01"), "Empty sunny villa and pool, no key."),
                         ("P_BINGO", S("E02"), "Empty bingo hall with empty seats and tables."),
                         ("P_VILLAGE", P("G01_sn1"), "Empty sunny village street."),
                         ("P_STADIUM", S("J02"), "Empty sunny pitch; the crowd in the stands stays, the player is removed."),
                         ("P_POLL", S("L01"), "Empty polling hall with empty booths.")]:
    add(PL(name), [ref], f"{PLATE} {extra}")
