#!/usr/bin/env python3
"""
SENTI-MIND Training Data Generator (v3)
Uses realistic, varied mental health sentences across 7 categories.
Includes hard-negative examples in the Normal class to combat false positives.
"""

import csv
import random
from pathlib import Path

random.seed(42)

# ---------------------------------------------------------------------------
# DEPRESSION
# ---------------------------------------------------------------------------
DEPRESSION_SENTENCES = [
    "I feel empty inside and nothing brings me joy anymore",
    "Getting out of bed every morning feels impossible",
    "I've stopped caring about things I used to love",
    "The sadness never goes away no matter what I do",
    "I feel like a burden to everyone around me",
    "I don't see any point in trying anymore",
    "Everything feels hopeless and bleak",
    "I wake up feeling exhausted even after eight hours of sleep",
    "I've been isolating myself from friends and family lately",
    "I feel numb and disconnected from everything",
    "I can't find the motivation to do even basic tasks",
    "Life feels meaningless and I don't know why",
    "I've been crying for no apparent reason every day",
    "I look in the mirror and hate what I see",
    "I feel like I'm trapped in a dark hole I can't escape",
    "I have no energy even for things I used to enjoy",
    "I feel invisible like no one really sees me",
    "I can't concentrate at work because my mind is just blank",
    "I've been skipping meals because I have no appetite",
    "I feel like I'm failing at everything no matter how hard I try",
    "The future looks dark and I can't see a way through",
    "I feel ashamed for feeling this way but I can't stop",
    "Simple things like showering feel like climbing a mountain",
    "I've lost interest in hobbies I used to care deeply about",
    "I feel so alone even when I'm surrounded by people",
    "I've been sleeping too much but never feel rested",
    "I feel like everyone would be better off without me",
    "I used to enjoy cooking but now even that feels overwhelming",
    "I keep thinking about all my failures and regrets",
    "My depression makes it hard to hold a conversation",
    "I feel like the color has drained out of my life",
    "I can barely make it through the day without crying",
    "I withdraw from social situations because I feel so low",
    "My mood has been consistently dark for weeks now",
    "I feel frozen like I can't move or think clearly",
    "Every day feels the same gloomy and pointless",
    "I stopped going to the gym even though it used to make me happy",
    "The weight of sadness feels physical like carrying a heavy load",
    "I've been avoiding phone calls and messages from friends",
    "I feel like I'm watching my life happen from the outside",
    "Nothing excites me anymore everything feels flat",
    "I lost my sense of humor I used to laugh all the time",
    "I feel guilty for being depressed like I should just snap out of it",
    "Getting dressed in the morning feels like an enormous effort",
    "I've been staring at the ceiling for hours unable to sleep",
    "My thoughts are always negative no matter what good things happen",
    "I feel like I'm slowly disappearing",
    "I've turned down every invitation because I just can't face people",
    "My self-esteem is at an all-time low",
    "I used to have dreams and goals but they all feel pointless now",
    "Some days I don't eat anything because I just forget",
    "I feel profoundly alone in this struggle",
    "I've been irritable and short-tempered which isn't like me",
    "I feel like I'm grieving something I can't name",
    "My body aches and I think it's the depression",
    "I can't finish tasks I start because my focus is completely gone",
    "Every little setback feels catastrophic",
    "I feel like deadwood just drifting with no direction",
    "I don't call my friends anymore because I don't want to drag them down",
    "The darkness in my mind never fully lifts even on good days",
]

# ---------------------------------------------------------------------------
# ANXIETY
# ---------------------------------------------------------------------------
ANXIETY_SENTENCES = [
    "My heart races when I think about going to work tomorrow",
    "I can't stop worrying about things that haven't happened yet",
    "I feel a constant sense of dread that won't go away",
    "I had a panic attack in the grocery store yesterday",
    "I overthink every conversation I have and replay it for hours",
    "My hands shake when I'm in social situations",
    "I avoid crowded places because they make me panic",
    "I can't sleep because my mind won't stop racing",
    "I'm terrified of making mistakes at work",
    "I check the door lock five times before I can leave the house",
    "My stomach is always in knots when I have to meet new people",
    "I feel like something terrible is about to happen at any moment",
    "I've been having shortness of breath even when I'm not exercising",
    "I can't make decisions because I'm scared of choosing wrong",
    "I rehearse phone calls in my head before I make them",
    "I feel on edge all the time like I'm waiting for disaster",
    "My mind catastrophizes every situation automatically",
    "I got so anxious about a presentation that I called in sick",
    "I avoid driving on the highway because I fear losing control",
    "I feel dizzy and lightheaded when anxiety hits",
    "I wash my hands repeatedly because I'm afraid of germs",
    "I can feel my pulse in my throat when I'm anxious",
    "Small uncertainties send me into a spiral of worry",
    "I'm afraid of embarrassing myself in front of others",
    "I've turned down job opportunities because they made me too nervous",
    "My anxiety makes it hard to eat in public",
    "I feel like I'm constantly bracing for something bad",
    "I tense up my whole body and don't even realize I'm doing it",
    "I can't enjoy social events because I'm too busy worrying",
    "My anxiety makes me cancel plans at the last minute",
    "I feel overwhelmed by noise and busy environments",
    "I worry about my health constantly even when tests come back normal",
    "I need constant reassurance that I haven't offended someone",
    "I feel unsafe even at home sometimes",
    "The anticipation of events is always worse than the events themselves",
    "I have racing thoughts that feel completely out of control",
    "I avoid elevators because I'm scared of being trapped",
    "My anxiety spikes when I receive unexpected messages",
    "I feel like I'm always walking on a tightrope",
    "I struggle to be present because I'm always worrying about the future",
    "My chest tightens every Sunday night because of Monday",
    "I set multiple alarms because I'm terrified of oversleeping",
    "I've been grinding my teeth from tension",
    "Even good news triggers a sense of waiting for the other shoe to drop",
    "Crowds make me feel claustrophobic and panicky",
    "I startle very easily at sudden noises",
    "I worry that I have a serious illness even when doctors reassure me",
    "My anxiety is exhausting because it never fully stops",
    "I cancel social plans because the anxiety feels like too much",
    "I feel paralyzed by anticipatory anxiety",
    "My palms get sweaty before any kind of performance",
    "I overthink texts before sending them",
    "I feel nervous around authority figures even when I've done nothing wrong",
    "My anxiety surfaces as irritability and snapping at loved ones",
    "I avoid conflict so strongly that I let people walk over me",
    "I can't delegate because I'm afraid things won't be done correctly",
    "My heart pounds when the phone rings unexpectedly",
    "I fear losing control of myself in public",
    "The anxiety feels like a background hum that never stops",
    "I rehearse worst-case scenarios in my head constantly",
]

# ---------------------------------------------------------------------------
# SUICIDAL
# ---------------------------------------------------------------------------
SUICIDAL_SENTENCES = [
    "I want to end my life I can't take this anymore",
    "I've been thinking about suicide every day",
    "Nobody would miss me if I was gone",
    "I have a plan to kill myself",
    "I want to disappear permanently",
    "I've been researching methods to end my life",
    "I told my friend goodbye because I don't think I'll be here tomorrow",
    "I feel like death is the only way to escape this pain",
    "I've written letters to my family just in case",
    "I'm going to end it all soon",
    "I don't want to wake up tomorrow",
    "I gave away my most important belongings this week",
    "Life isn't worth living anymore",
    "I think about killing myself every single night",
    "The only thought that gives me relief is thinking about not being here",
    "I've decided I can't go on living like this",
    "I've been stockpiling pills",
    "I'm a burden and my family would thrive without me",
    "I don't see any reason to stay alive",
    "I'm ready to die",
    "I want to fall asleep and never wake up",
    "I'm planning to hurt myself tonight",
    "I've been searching for ways to end my life online",
    "I feel like everyone would be better off if I wasn't here",
    "I can't see the point of continuing",
    "I'm considering taking my own life as the only relief",
    "I feel completely trapped and see no other exit",
    "I've been driving recklessly hoping something happens",
    "I feel like I deserve to die",
    "I've said goodbye to the people I care about",
    "There's no future for me and I accept that now",
    "I hurt myself earlier today to cope",
    "I'm done suffering I'll end it tonight",
    "I keep cutting myself to feel something",
    "I think about how and when I'll do it",
    "I've set a date to end my life",
    "I'm not afraid of dying anymore",
    "The pain is unbearable and death would be a relief",
    "I want to harm myself when things get bad",
    "I told a hotline I was going to kill myself",
    "I feel suicidal and I can't stop these thoughts",
    "I've self-harmed multiple times this week",
    "My only way out feels like ending it",
    "I reached out to no one because there's no point",
    "I'm invisible to everyone and I should just disappear",
    "I can't fight anymore I'm ready to go",
    "I have a note already written",
    "I'm going to end this pain permanently",
    "I told my therapist I don't want to be alive",
    "I don't value my life anymore",
    "I'm planning to overdose on medication",
    "I feel suicidal every time I'm alone",
    "I've been saying my last goodbyes",
    "I'm going to walk into traffic",
    "The thought of suicide is the only thing that calms me down",
    "I attempted to harm myself last night",
    "I keep a knife near me just in case",
    "I've been crying and thinking about ending it all",
    "There's no escape except death",
    "I need someone to stop me from hurting myself",
]

# ---------------------------------------------------------------------------
# STRESS
# ---------------------------------------------------------------------------
STRESS_SENTENCES = [
    # Negation-stress patterns (model must distinguish from Suicidal)
    "I'm not suicidal just completely overwhelmed with work stress right now",
    "I'm not feeling suicidal at all I'm just stressed out of my mind",
    "I'm not thinking about harming myself I'm just exhausted from work pressure",
    "I'm not suicidal but I am really struggling with burnout and stress",
    "I don't want to die I just desperately need a break from work",
    "I'm not in crisis I'm just massively stressed about everything right now",
    "I'm not having dark thoughts I'm just so overwhelmed by responsibilities",
    # Core stress sentences
    "Work is completely overwhelming me right now",
    "I can't keep up with all my deadlines and responsibilities",
    "I haven't had a day off in three weeks and I'm burning out",
    "My boss keeps piling more work on me and I can't say no",
    "I'm juggling too many things at once and dropping the ball",
    "The pressure at work is making me physically ill",
    "I never have time for myself anymore",
    "I snap at my family because I'm so stressed",
    "I can't switch off from work even when I'm at home",
    "My to-do list just keeps growing and never shrinks",
    "I've been getting headaches from carrying so much tension",
    "I feel like I'm always behind no matter how hard I work",
    "Financial stress is keeping me up at night",
    "I'm stressed about paying rent next month",
    "I feel crushed by the expectations everyone has of me",
    "I haven't had a proper meal this week because I'm so busy",
    "My shoulders and neck are constantly tense from stress",
    "I feel like I'm drowning in obligations",
    "I take on too much and then feel overwhelmed",
    "The workload is unreasonable and I feel trapped",
    "I'm so stressed I've developed a twitch in my eye",
    "Family problems and work stress are happening at the same time",
    "I haven't slept well in weeks because of the pressure",
    "I feel like I'm on a hamster wheel that never stops",
    "I'm running on caffeine and stress",
    "I have so many responsibilities I don't know where to start",
    "I'm stressed about my performance review coming up",
    "I feel like I can't catch a breath there's always something new",
    "My anxiety about work is affecting my personal relationships",
    "I'm burnt out but I can't afford to slow down",
    "The constant stress is making my hair fall out",
    "I feel overwhelmed by chores at home and demands at work",
    "My stress is through the roof with this project deadline",
    "I haven't exercised in months because I have no time",
    "I feel like I carry all the responsibility and no one helps",
    "The commute on top of work stress is breaking me",
    "I procrastinate because I'm so overwhelmed I freeze",
    "I'm dealing with a difficult coworker and it's adding to my load",
    "My stress is affecting my ability to concentrate",
    "I used to enjoy my job but now it just feels like a grind",
    "I feel guilty taking breaks even when I really need one",
    "Multiple deadlines hit at the same time and I panicked",
    "I'm stressed about my kids' school and my own workload",
    "The pressure to be perfect is crushing me",
    "I've been grinding my teeth at night from work stress",
    "My stress levels are so high my doctor told me to slow down",
    "I feel like there's no light at the end of the tunnel with work",
    "I'm spread so thin I feel like I'm barely present for anyone",
    "I haven't taken a real vacation in two years",
    "I feel like a hamster constantly running but going nowhere",
    "I missed an important deadline and felt sick with stress",
    "I'm dealing with family drama and work pressure simultaneously",
    "Money problems and job insecurity are weighing on me",
    "I've been irritable and impatient because of chronic stress",
    "I'm stressed about a big exam coming up next week",
    "I feel stretched too thin between all my commitments",
    "The workplace culture is toxic and it's stressing me out",
    "I feel like I can never fully relax",
    "I'm running on empty and I can't see when things will ease up",
    "Chronic stress is affecting my physical health now",
]

# ---------------------------------------------------------------------------
# BIPOLAR
# ---------------------------------------------------------------------------
BIPOLAR_SENTENCES = [
    "I cycle between feeling invincible and then completely worthless",
    "I spent thousands of dollars in a weekend and now regret it",
    "I barely slept for three days and felt amazing until I crashed",
    "My energy swings wildly from too much to barely any",
    "I feel euphoric and untouchable then suddenly suicidal",
    "During my highs I make reckless decisions I later regret",
    "I've had periods where I barely needed sleep and felt superhuman",
    "My moods shift so fast it confuses everyone around me",
    "I started five projects during my manic phase and finished none",
    "I was extremely irritable and snappy for no obvious reason",
    "I went on a shopping spree during my high and maxed out my credit card",
    "I feel grandiose sometimes like I have special abilities",
    "My lows are devastating and my highs scare me",
    "I talk so fast during my highs that people can't follow me",
    "I've been hospitalized twice for manic episodes",
    "My thoughts race so fast I can't catch them during a high",
    "I feel like two different people depending on which phase I'm in",
    "I engaged in risky sexual behavior during my last manic episode",
    "The highs feel incredible but the crashes are catastrophic",
    "I was diagnosed with bipolar disorder and I'm struggling to accept it",
    "I drive dangerously fast when I'm manic",
    "I feel like I can conquer the world and then hit rock bottom",
    "My relationships suffer because my behavior is so unpredictable",
    "My manic phases leave me with regrets and my depressive phases with despair",
    "I go from laughing hysterically to crying in the space of an hour",
    "I've quit my job impulsively during a manic phase before",
    "I feel a false sense of confidence during highs that leads to bad choices",
    "My energy level fluctuates so dramatically it's hard to plan anything",
    "During depressive phases I can't get out of bed and during highs I can't sit still",
    "I've been told I become a different person when I'm manic",
    "I have extreme mood swings that disrupt my daily life",
    "I was irritable and agitated for days then suddenly crashed into depression",
    "I feel elated and powerful then the crash hits and I want to die",
    "My spending habits during manic phases have caused major problems",
    "I can't maintain friendships because of how unpredictable my moods are",
    "I have trouble sleeping during mania which makes the phase worse",
    "I feel all-powerful during highs and utterly useless during lows",
    "My mood episodes have caused me to lose jobs and relationships",
    "I've been impulsive with alcohol during elevated moods",
    "The mixed states are the worst when I'm energized but miserable",
    "I feel my mood cycling and I can't control it",
    "My thoughts during mania are so loud and fast it feels like chaos",
    "I was on a high for two weeks and then fell into deep depression",
    "I have rapid cycling episodes that make me exhausted",
    "I feel like I'm on a rollercoaster I can't get off",
    "I made a major life decision impulsively during a manic phase",
    "During a manic phase I feel like I don't need food or rest",
    "My partner says they never know which version of me they'll get",
    "I have grandiose ideas when I'm manic that seem delusional in retrospect",
    "The depression after a manic high is like falling off a cliff",
    "I feel like my brain is broken because it swings so violently",
    "I took out a loan impulsively during my last high",
    "My moods are extreme and I struggle to regulate them",
    "I feel superhuman during my manic phase until it collapses",
    "I was irritable and combative for days which isn't my baseline",
    "I've been working on managing my bipolar disorder with therapy",
    "My mania makes me feel creative and brilliant but leads to chaos",
    "I go from not sleeping to sleeping 15 hours a day cyclically",
    "I've hurt people I love when manic and I regret it deeply",
    "My mood disorder makes it hard to live a stable life",
]

# ---------------------------------------------------------------------------
# PERSONALITY DISORDER
# ---------------------------------------------------------------------------
PERSONALITY_DISORDER_SENTENCES = [
    # Identity instability — the core marker distinguishing PD from depression
    "I genuinely don't know who I am my identity feels like it doesn't exist",
    "My sense of self completely changes depending on who I'm with",
    "I feel disconnected from who I am like I have no real identity",
    "I don't know what my values are they seem to shift constantly",
    "I feel like a different person around different people and I can't stop it",
    "I have no stable sense of self it just shifts based on the situation",
    "I feel disconnected from myself and I genuinely don't know who I am",
    "I can't answer the question of who I am my identity is completely unstable",
    "I feel like I don't have a core self I just mirror whoever I'm around",
    "My personality changes so drastically between situations it scares me",
    # Abandonment fear
    "I feel empty inside like there's nothing at my core",
    "My relationships are always chaotic intense and then suddenly over",
    "I don't know who I really am my sense of self keeps shifting",
    "I push people away before they can abandon me",
    "I idealize people and then devalue them when they disappoint me",
    "I feel intense rage over things others consider minor",
    "I'm terrified of being left alone even for a few hours",
    "I see people as either perfect or completely terrible there's no middle ground",
    "I engage in impulsive behaviors like binge eating and reckless spending",
    "I feel like nobody truly understands or knows me",
    "My identity changes depending on who I'm around",
    "Relationships feel like a constant source of crisis for me",
    "I feel paranoid and suspicious of everyone's motives",
    "I sometimes feel like I'm not real like I'm watching myself from outside",
    "I have urges to self-harm when I feel abandoned",
    "I feel chronically empty even when things seem fine on the surface",
    "I switch from loving someone to hating them very quickly",
    "My emotions are like a rollercoaster and I can't control them",
    "I struggle with a deeply unstable sense of who I am",
    "I feel detached from reality sometimes and it scares me",
    "My intense fear of abandonment destroys my relationships",
    "I act impulsively and recklessly when emotionally overwhelmed",
    "I feel suspicious of people even when they've done nothing wrong",
    "My mood changes dramatically in response to relationship stress",
    "I feel profoundly empty when I'm not in a relationship",
    "I dissociate and feel like things around me aren't real",
    "I have a history of unstable and turbulent relationships",
    "I feel like different people in different situations",
    "I have outbursts of anger that feel completely out of proportion",
    "I'm afraid that the people I love will eventually leave me",
    "I create crises unconsciously because I can't tolerate calm",
    "I feel unreal and question whether I exist",
    "I need constant reassurance from partners that they love me",
    "I've been told I'm manipulative but that's not my intention",
    "I feel rage that comes from nowhere and shocks even me",
    "I hurt myself when I'm overwhelmed with abandonment feelings",
    "My sense of self is so unstable I don't know my own values",
    "I feel emotions far more intensely than people around me",
    "I've had several suicide threats during relationship problems",
    "I trust people completely then become convinced they're against me",
    "I feel like I'm not a real person just a reflection of others",
    "My intense attachment to people terrifies them away",
    "I feel bored and empty when life is stable which scares me",
    "I have chronic feelings of emptiness that nothing fills",
    "I've destroyed friendships over perceived slights",
    "I oscillate between wanting to be close and pushing people away",
    "I feel like I wear different masks for different people",
    "My impulsivity has gotten me into serious trouble",
    "I feel an intense fear of being truly alone",
    "I feel split between loving and loathing myself constantly",
    "I've been diagnosed with borderline personality disorder",
    "People say I'm too intense and it pushes them away",
    "I feel like my personality is unstable and I can't grasp who I am",
    "I go to extremes in relationships obsessive closeness or sudden distance",
    "I feel completely shattered when someone I care about criticizes me",
    "I sometimes question whether my memories of events are accurate",
    "I feel detached and dissociated when I'm very stressed",
    "My pattern of unstable relationships has repeated throughout my life",
    "I feel victimized even when others mean well",
    "I see everything in black and white which causes huge problems",
]

# ---------------------------------------------------------------------------
# NORMAL — includes hard negatives (sentences with clinical-sounding words
# that are genuinely fine, to combat false positives)
# ---------------------------------------------------------------------------
NORMAL_SENTENCES = [
    "I had a really productive day at work today",
    "I'm feeling great and looking forward to the weekend",
    "Just got back from a morning run and I feel amazing",
    "I cooked a delicious meal and enjoyed it with my family",
    "I finished a big project and I'm proud of the result",
    "I'm feeling content and at peace with where I am in life",
    "I had a wonderful lunch with a good friend today",
    "I'm excited about my vacation coming up next week",
    "I learned something new today and it made me feel good",
    "Life is going well and I'm genuinely happy",
    "I had a great workout and I feel energized",
    "I'm grateful for my supportive family and friends",
    "I got a promotion at work and I'm really pleased",
    "I'm in a good mood today for no special reason",
    "I enjoyed a relaxing evening reading a book",
    "I feel balanced and healthy right now",
    "I spent the afternoon gardening and it made me happy",
    "I'm feeling optimistic about the future",
    "I had a full night of sleep and feel completely rested",
    "My relationship is going really well and I feel supported",
    "I helped a stranger today and it lifted my spirits",
    "I'm feeling confident about my upcoming interview",
    "I had a fun game night with friends",
    "I finished my to-do list and feel accomplished",
    "I'm in a great headspace and things feel manageable",
    "I treated myself to a nice coffee and enjoyed every sip",
    "I watched a funny movie and laughed a lot",
    "I'm feeling motivated and ready to tackle my goals",
    "I had a nice conversation with my parents today",
    "I'm doing well overall just living my life",
    # Hard negatives — contain clinical-sounding words but are Normal
    "My friend's mood was a bit off but she's fine now",
    "My friend's stress about exams is pretty normal for this time of year",
    "My brother's stress about his new job will ease once he settles in",
    "I can see my roommate's stress about exams but she'll get through it",
    "My colleague's anxiety about the presentation was understandable but she did great",
    "My sister's stress about her relationship resolved itself happily",
    "I told my therapist that my stress levels have actually improved",
    "I used to be anxious about flying but I've gotten over it",
    "We talked about depression in my psychology class today",
    "I was stressed about the exam but I passed with a good grade",
    "I felt nervous before my presentation but it went really well",
    "My colleague was talking about their bipolar disorder openly",
    "I worried about the project deadline but we finished on time",
    "I felt a bit low last week but I'm much better now",
    "I was feeling hopeless about the job search but got an offer today",
    "I've been managing my stress much better with exercise",
    "I had a hard time but I've really turned things around",
    "My mood has been stable and positive this month",
    "I talked to a counselor and I'm doing much better now",
    "I felt overwhelmed but I asked for help and things got better",
    "My anxiety about the move was unfounded it went smoothly",
    "I used to struggle with self-worth but therapy helped a lot",
    "I was in a dark place last year but I've recovered well",
    "I had some stress at work but it resolved itself",
    "I felt a bit burnt out so I took a holiday and I'm refreshed",
    "I talked about suicidal thoughts I had years ago with my therapist",
    "I'm no longer depressed thanks to good support and treatment",
    "My panic attacks have stopped since I started medication",
    "I've been learning about mental health to help my friend",
    "I had mild anxiety before the wedding but it was manageable",
    "The therapy really helped me process my difficult emotions",
    "I felt disconnected for a while but reconnected with my friends",
    "I'm in recovery from my depression and making real progress",
    "I was worried I might be bipolar but my doctor ruled it out",
    "I felt anxious that day but took deep breaths and it passed",
]

# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def sample_sentences(sentences: list[str], count: int, label: str) -> list[tuple[str, str]]:
    """Sample `count` unique sentences from the pool, cycling if needed."""
    result = []
    pool = sentences[:]
    random.shuffle(pool)
    while len(result) < count:
        if not pool:
            pool = sentences[:]
            random.shuffle(pool)
        result.append((pool.pop(), label))
    return result


def main():
    SAMPLES_PER_CLASS = 200

    print("Generating SENTI-MIND v3 training data...")

    all_data: list[tuple[str, str]] = []

    categories = [
        (DEPRESSION_SENTENCES, "Depression"),
        (ANXIETY_SENTENCES, "Anxiety"),
        (SUICIDAL_SENTENCES, "Suicidal"),
        (STRESS_SENTENCES, "Stress"),
        (BIPOLAR_SENTENCES, "Bipolar"),
        (PERSONALITY_DISORDER_SENTENCES, "Personality disorder"),
        (NORMAL_SENTENCES, "Normal"),
    ]

    for sentences, label in categories:
        samples = sample_sentences(sentences, SAMPLES_PER_CLASS, label)
        all_data.extend(samples)
        print(f"  {label}: {len(samples)} samples (from pool of {len(sentences)})")

    # --- Short-text augmentation ---
    # Real journal entries are often 1-5 words. The model fails on these.
    # Adding targeted short-text examples per class improves short-input accuracy.
    short_text_samples: list[tuple[str, str]] = [
        # Depression
        ("feeling low", "Depression"), ("so empty", "Depression"), ("nothing matters", "Depression"),
        ("completely numb", "Depression"), ("no energy", "Depression"), ("lost motivation", "Depression"),
        ("crying again", "Depression"), ("feel invisible", "Depression"), ("stuck in darkness", "Depression"),
        # Anxiety
        ("panic attack", "Anxiety"), ("cant breathe", "Anxiety"), ("always worried", "Anxiety"),
        ("mind racing", "Anxiety"), ("chest tight", "Anxiety"), ("scared again", "Anxiety"),
        ("constant dread", "Anxiety"), ("overthinking everything", "Anxiety"), ("on edge", "Anxiety"),
        # Suicidal
        ("want to die", "Suicidal"), ("end it all", "Suicidal"), ("no point anymore", "Suicidal"),
        ("cant go on", "Suicidal"), ("done with life", "Suicidal"), ("ready to go", "Suicidal"),
        # Stress
        ("completely overwhelmed", "Stress"), ("too much pressure", "Stress"), ("burning out", "Stress"),
        ("exhausted from work", "Stress"), ("cant cope", "Stress"), ("deadline stress", "Stress"),
        ("no time to breathe", "Stress"), ("running on empty", "Stress"),
        # Bipolar
        ("mood swings again", "Bipolar"), ("manic episode", "Bipolar"), ("highs and lows", "Bipolar"),
        ("crashed after euphoria", "Bipolar"), ("cycling badly", "Bipolar"),
        # Personality disorder
        ("dont know who I am", "Personality disorder"), ("pushing everyone away", "Personality disorder"),
        ("intense abandonment fear", "Personality disorder"), ("identity confusion", "Personality disorder"),
        # Normal
        ("good day today", "Normal"), ("feeling okay", "Normal"), ("life is fine", "Normal"),
        ("nothing special", "Normal"), ("all good", "Normal"), ("relaxed today", "Normal"),
        ("happy and content", "Normal"), ("productive day", "Normal"),
    ]
    all_data.extend(short_text_samples)
    print(f"  Short-text augmentation: {len(short_text_samples)} samples added")

    random.shuffle(all_data)

    output_path = Path(__file__).parent.parent / "data" / "Combined Data.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["statement", "status"])
        writer.writerows(all_data)

    total = len(all_data)
    print(f"\nTotal samples: {total} ({SAMPLES_PER_CLASS} per class × {len(categories)} classes + {len(short_text_samples)} short-text)")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
