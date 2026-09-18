import os
import re
import json
import time
import shutil
import requests

from pathlib import Path


# ================================================================
# CONFIGURATION
# ================================================================

REPO_ROOT = Path(".")

README_FILE = REPO_ROOT / "README.md"
STATS_FILE = REPO_ROOT / "stats.json"

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"


# ================================================================
# LEETCODE REQUEST HEADERS
# ================================================================

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}


# ================================================================
# SUPPORTED SOURCE FILES
# ================================================================

SOURCE_EXTENSIONS = {
    ".java",
    ".cpp",
    ".cc",
    ".cxx",
    ".c",
    ".py",
    ".js",
    ".ts",
    ".go",
    ".rs",
    ".kt"
}


# ================================================================
# DIRECTORIES TO IGNORE
# ================================================================

IGNORE_DIRS = {
    ".git",
    ".github",
    ".vscode",
    "__pycache__",
    "node_modules",
    ".idea"
}


# ================================================================
# FILES TO IGNORE
# ================================================================

IGNORE_FILES = {
    "README.md",
    "stats.json",
    "generate_readme.py"
}


# ================================================================
# LEETCODE TOPIC PRIORITY
#
# Used when a problem has multiple LeetCode tags.
# The first matching topic becomes the primary domain.
# ================================================================

TOPIC_PRIORITY = [

    "Array",
    "String",
    "Hash Table",
    "Two Pointers",
    "Binary Search",
    "Bit Manipulation",
    "Math",
    "Prefix Sum",
    "Sliding Window",
    "Sorting",
    "Stack",
    "Queue",
    "Linked List",
    "Tree",
    "Trie",
    "Heap",
    "Graph",
    "Greedy",
    "Dynamic Programming",
    "Backtracking",
    "Divide and Conquer",
    "Recursion",
    "Simulation",
    "String Matching",
    "Number Theory",
    "Boyer-Moore String-Search Algorithm",
    "Knuth-Morris-Pratt Algorithm",
    "Z Algorithm"
]


# ================================================================
# DOMAIN FOLDER NAMES
#
# Maps LeetCode topic name -> GitHub folder name
# ================================================================

DOMAIN_FOLDER_NAMES = {

    "Array": "Array",

    "String": "String",

    "Hash Table": "Hash-Table",

    "Two Pointers": "Two-Pointers",

    "Binary Search": "Binary-Search",

    "Bit Manipulation": "Bit-Manipulation",

    "Math": "Math",

    "Prefix Sum": "Prefix-Sum",

    "Sliding Window": "Sliding-Window",

    "Sorting": "Sorting",

    "Stack": "Stack",

    "Queue": "Queue",

    "Linked List": "Linked-List",

    "Tree": "Tree",

    "Trie": "Trie",

    "Heap": "Heap",

    "Graph": "Graph",

    "Greedy": "Greedy",

    "Dynamic Programming": "Dynamic-Programming",

    "Backtracking": "Backtracking",

    "Divide and Conquer": "Divide-and-Conquer",

    "Recursion": "Recursion",

    "Simulation": "Simulation",

    "String Matching": "String-Matching",

    "Number Theory": "Number-Theory",

    "Boyer-Moore String-Search Algorithm":
        "Boyer-Moore-String-Search-Algorithm",

    "Knuth-Morris-Pratt Algorithm":
        "Knuth-Morris-Pratt-Algorithm",

    "Z Algorithm":
        "Z-Algorithm"
}


# ================================================================
# LANGUAGE DETECTION
# ================================================================

LANGUAGE_MAP = {

    ".java": "Java",

    ".cpp": "C++",

    ".cc": "C++",

    ".cxx": "C++",

    ".c": "C",

    ".py": "Python",

    ".js": "JavaScript",

    ".ts": "TypeScript",

    ".go": "Go",

    ".rs": "Rust",

    ".kt": "Kotlin"
}


# ================================================================
# SLUG NORMALIZATION
# ================================================================

def normalize_slug(value):

    value = value.strip().lower()

    # Remove leading problem number
    value = re.sub(
        r"^\d+[\s._-]+",
        "",
        value
    )

    value = value.replace("_", "-")

    value = re.sub(
        r"\s+",
        "-",
        value
    )

    value = re.sub(
        r"[^a-z0-9-]",
        "",
        value
    )

    value = re.sub(
        r"-+",
        "-",
        value
    )

    return value.strip("-")


# ================================================================
# CHECK WHETHER FOLDER IS A PROBLEM FOLDER
# ================================================================

def contains_source_code(folder):

    try:

        for file in folder.iterdir():

            if not file.is_file():
                continue

            if file.name in IGNORE_FILES:
                continue

            if file.suffix.lower() in SOURCE_EXTENSIONS:
                return True

    except Exception:
        return False

    return False


# ================================================================
# FIND ALL PROBLEM FOLDERS
#
# IMPORTANT:
# This scans BOTH:
#
# Array/two-sum/
#
# AND:
#
# two-sum/
#
# ================================================================

def find_problem_folders():

    found = []

    for root, dirs, files in os.walk(REPO_ROOT):

        root_path = Path(root)

        # Remove ignored directories
        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS
            and not d.startswith(".")
        ]

        # Ignore hidden root
        if any(part.startswith(".") for part in root_path.parts):
            continue

        # Root itself could be a problem folder
        if root_path != REPO_ROOT:

            source_found = False

            for filename in files:

                file_path = root_path / filename

                if filename in IGNORE_FILES:
                    continue

                if file_path.suffix.lower() in SOURCE_EXTENSIONS:

                    source_found = True
                    break

            if source_found:

                found.append(root_path)

                # Do not scan inside a problem folder
                dirs[:] = []

    return found


# ================================================================
# GET LANGUAGE
# ================================================================

def get_language(folder):

    languages = []

    try:

        for file in folder.iterdir():

            if not file.is_file():
                continue

            extension = file.suffix.lower()

            if extension in LANGUAGE_MAP:

                languages.append(
                    LANGUAGE_MAP[extension]
                )

    except Exception:
        pass

    if not languages:
        return "Unknown"

    # Remove duplicates while keeping order
    languages = list(dict.fromkeys(languages))

    return ", ".join(languages)


# ================================================================
# GET LEETCODE SLUG
# ================================================================

def get_slug(folder):

    return normalize_slug(folder.name)


# ================================================================
# LEETCODE API
# ================================================================

def get_problem(slug):

    query = """
    query questionData($titleSlug: String!) {

        question(titleSlug: $titleSlug) {

            questionFrontendId

            title

            titleSlug

            difficulty

            topicTags {
                name
            }
        }
    }
    """

    payload = {

        "query": query,

        "variables": {
            "titleSlug": slug
        }
    }


    # Retry several times
    for attempt in range(3):

        try:

            response = requests.post(
                LEETCODE_GRAPHQL,
                json=payload,
                headers=HEADERS,
                timeout=30
            )

            if response.status_code != 200:

                print(
                    f"API status {response.status_code} "
                    f"for {slug}"
                )

                time.sleep(2)

                continue


            data = response.json()


            if "data" not in data:

                time.sleep(2)

                continue


            question = data["data"].get("question")


            if question:

                return question


            print(
                f"No LeetCode metadata found for: {slug}"
            )

            return None


        except Exception as error:

            print(
                f"API error for {slug}: {error}"
            )

            time.sleep(2)


    return None


# ================================================================
# TITLE FROM SLUG
#
# Used when LeetCode API is unavailable.
# ================================================================

def title_from_slug(slug):

    words = slug.replace("-", " ").split()

    return " ".join(
        word.capitalize()
        for word in words
    )


# ================================================================
# GET PRIMARY DOMAIN
#
# If multiple tags exist, choose according to TOPIC_PRIORITY.
# ================================================================

def get_primary_domain(tags, current_parent=None):

    # ------------------------------------------------------------
    # First priority:
    # If current parent folder is already one of the valid
    # LeetCode domains, keep it if it matches a tag.
    # ------------------------------------------------------------

    if current_parent:

        for topic, folder_name in DOMAIN_FOLDER_NAMES.items():

            if current_parent.lower() == folder_name.lower():

                if topic in tags:

                    return topic


    # ------------------------------------------------------------
    # Second priority:
    # Use predefined topic priority.
    # ------------------------------------------------------------

    for topic in TOPIC_PRIORITY:

        if topic in tags:

            return topic


    # ------------------------------------------------------------
    # No known tag
    # ------------------------------------------------------------

    return "Uncategorized"


# ================================================================
# GET CURRENT DOMAIN
# ================================================================

def get_current_domain(folder):

    if folder.parent == REPO_ROOT:

        return None

    parent_name = folder.parent.name

    for topic, folder_name in DOMAIN_FOLDER_NAMES.items():

        if parent_name.lower() == folder_name.lower():

            return topic

    return None


# ================================================================
# MOVE PROBLEM INTO CORRECT DOMAIN
# ================================================================

def organize_problem(folder, primary_domain):

    if primary_domain == "Uncategorized":

        return folder


    domain_folder_name = DOMAIN_FOLDER_NAMES.get(
        primary_domain,
        primary_domain
    )


    target_domain = REPO_ROOT / domain_folder_name


    target_domain.mkdir(
        parents=True,
        exist_ok=True
    )


    target_folder = target_domain / folder.name


    # Already in correct place
    if folder.resolve() == target_folder.resolve():

        return target_folder


    # ------------------------------------------------------------
    # If target exists, don't overwrite.
    # ------------------------------------------------------------

    if target_folder.exists():

        print(
            f"Target already exists: {target_folder}"
        )

        return target_folder


    print("")
    print("MOVING")
    print(f"FROM : {folder}")
    print(f"TO   : {target_folder}")


    try:

        shutil.move(
            str(folder),
            str(target_folder)
        )

        return target_folder

    except Exception as error:

        print(
            f"Could not move {folder}: {error}"
        )

        return folder


# ================================================================
# COLLECT PROBLEMS
# ================================================================

def collect_problems():

    print("")
    print("==============================================")
    print("SCANNING LEETCODE SOLUTIONS")
    print("==============================================")
    print("")


    folders = find_problem_folders()


    print(
        f"Found {len(folders)} solution folders"
    )


    problems = {}


    for folder in folders:

        slug = get_slug(folder)


        if not slug:
            continue


        # --------------------------------------------------------
        # Avoid duplicate folders
        # --------------------------------------------------------

        if slug in problems:

            print(
                f"Duplicate ignored: {slug}"
            )

            continue


        print(
            f"Fetching: {slug}"
        )


        # --------------------------------------------------------
        # Fetch LeetCode metadata
        # --------------------------------------------------------

        metadata = get_problem(slug)


        # --------------------------------------------------------
        # API FAILED
        #
        # DO NOT SKIP THE PROBLEM.
        # This is important for correct total count.
        # --------------------------------------------------------

        if metadata is None:

            print(
                f"Using fallback metadata for: {slug}"
            )


            number = 999999

            title = title_from_slug(slug)

            difficulty = "Unknown"

            tags = []


        else:

            number = int(
                metadata["questionFrontendId"]
            )

            title = metadata["title"]

            difficulty = metadata["difficulty"]


            tags = [

                tag["name"]

                for tag in metadata.get(
                    "topicTags",
                    []
                )

            ]


        # --------------------------------------------------------
        # Current domain
        # --------------------------------------------------------

        current_domain = get_current_domain(
            folder
        )


        # --------------------------------------------------------
        # Primary domain
        # --------------------------------------------------------

        primary_domain = get_primary_domain(
            tags,
            current_domain
        )


        # --------------------------------------------------------
        # Language
        # --------------------------------------------------------

        language = get_language(
            folder
        )


        problems[slug] = {

            "number": number,

            "title": title,

            "slug": slug,

            "difficulty": difficulty,

            "language": language,

            "tags": tags,

            "primary_domain": primary_domain,

            "folder": str(folder)

        }


    return problems


# ================================================================
# ORGANIZE ALL PROBLEM FOLDERS
# ================================================================

def organize_all_problems(problems):

    print("")
    print("==============================================")
    print("ORGANIZING PROBLEM DOMAINS")
    print("==============================================")
    print("")


    for slug, problem in list(
        problems.items()
    ):

        folder = Path(
            problem["folder"]
        )


        primary_domain = problem[
            "primary_domain"
        ]


        # Folder may have moved already
        if not folder.exists():

            continue


        new_folder = organize_problem(
            folder,
            primary_domain
        )


        problem["folder"] = str(
            new_folder
        )


# ================================================================
# RE-SCAN AFTER MOVING
#
# This guarantees README uses the final folder paths.
# ================================================================

def update_folder_paths(problems):

    for slug, problem in problems.items():

        current_folder = Path(
            problem["folder"]
        )


        if current_folder.exists():

            continue


        domain = problem[
            "primary_domain"
        ]


        if domain == "Uncategorized":

            continue


        domain_folder = DOMAIN_FOLDER_NAMES.get(
            domain,
            domain
        )


        possible_folder = (
            REPO_ROOT
            / domain_folder
            / Path(problem["folder"]).name
        )


        if possible_folder.exists():

            problem["folder"] = str(
                possible_folder
            )


# ================================================================
# SORT PROBLEMS
# ================================================================

def sort_problems(problems):

    def sort_key(problem):

        number = problem["number"]

        if number == 999999:

            return (
                999999,
                problem["title"].lower()
            )

        return (
            number,
            problem["title"].lower()
        )


    return sorted(
        problems.values(),
        key=sort_key
    )


# ================================================================
# CREATE CATEGORY DATA
#
# A problem can appear in multiple categories because
# LeetCode itself can assign multiple tags.
# ================================================================

def create_categories(all_problems):

    categories = {}


    for problem in all_problems:

        tags = problem["tags"]


        for tag in tags:

            if tag not in categories:

                categories[tag] = []


            categories[tag].append(
                problem
            )


    # Sort every category
    for category in categories:

        categories[category].sort(
            key=lambda x: (
                x["number"],
                x["title"].lower()
            )
        )


    return categories


# ================================================================
# ORDER CATEGORIES
# ================================================================

def order_categories(categories):

    ordered = []


    # First use our preferred order
    for topic in TOPIC_PRIORITY:

        if topic in categories:

            ordered.append(topic)


    # Add unknown/new LeetCode topics
    for topic in sorted(categories):

        if topic not in ordered:

            ordered.append(topic)


    return ordered


# ================================================================
# README
# ================================================================

def generate_readme(all_problems):

    easy = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Easy"
    )


    medium = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Medium"
    )


    hard = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Hard"
    )


    unknown = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Unknown"
    )


    total = len(all_problems)


    categories = create_categories(
        all_problems
    )


    ordered_categories = order_categories(
        categories
    )


    readme = []


    # ============================================================
    # HEADER
    # ============================================================

    readme.append(
        "# LeetCode_Solution"
    )

    readme.append("")

    readme.append(
        "Automatically organized LeetCode solutions "
        "with GitHub Actions."
    )

    readme.append("")


    # ============================================================
    # OVERALL PROGRESS
    # ============================================================

    readme.append(
        "## 📊 Overall Progress"
    )

    readme.append("")

    readme.append(
        "| Difficulty | Solved |"
    )

    readme.append(
        "|---|---:|"
    )

    readme.append(
        f"| 🟢 Easy | {easy} |"
    )

    readme.append(
        f"| 🟡 Medium | {medium} |"
    )

    readme.append(
        f"| 🔴 Hard | {hard} |"
    )

    readme.append(
        f"| ⚪ Unknown | {unknown} |"
    )

    readme.append(
        f"| **Total Solved** | **{total}** |"
    )

    readme.append("")


    # ============================================================
    # DOMAIN SUMMARY
    # ============================================================

    readme.append(
        "## 📚 Domain Summary"
    )

    readme.append("")

    readme.append(
        "| Domain | Problems |"
    )

    readme.append(
        "|---|---:|"
    )


    domain_counts = {}


    for problem in all_problems:

        domain = problem[
            "primary_domain"
        ]

        domain_counts[domain] = (
            domain_counts.get(domain, 0)
            + 1
        )


    for domain in sorted(
        domain_counts,
        key=lambda x: (
            x == "Uncategorized",
            x.lower()
        )
    ):

        readme.append(
            f"| {domain} | "
            f"{domain_counts[domain]} |"
        )


    readme.append("")


    # ============================================================
    # COMPLETE PROBLEM LIST
    #
    # Each problem appears ONLY ONCE here.
    # ============================================================

    readme.append(
        "## 📋 Complete Problem List"
    )

    readme.append("")

    readme.append(
        "| # | Problem | LeetCode | "
        "Language | Difficulty | Domain |"
    )

    readme.append(
        "|---:|---|---|---|---|---|"
    )


    for problem in all_problems:

        number = problem["number"]

        title = problem["title"]

        slug = problem["slug"]

        language = problem["language"]

        difficulty = problem["difficulty"]

        domain = problem[
            "primary_domain"
        ]

        folder = Path(
            problem["folder"]
        )


        relative_folder = folder.as_posix()


        solution_link = (
            f"./{relative_folder}"
        )


        if number != 999999:

            leetcode_link = (
                f"https://leetcode.com/problems/"
                f"{slug}/"
            )

            leetcode_text = (
                f"LeetCode #{number}"
            )

        else:

            leetcode_link = (
                f"https://leetcode.com/problems/"
                f"{slug}/"
            )

            leetcode_text = "LeetCode"


        readme.append(

            f"| {number if number != 999999 else '-'} | "
            f"[{title}]({solution_link}) | "
            f"[{leetcode_text}]({leetcode_link}) | "
            f"{language} | "
            f"{difficulty} | "
            f"{domain} |"

        )


    readme.append("")


    # ============================================================
    # DOMAIN-WISE PROBLEM LIST
    # ============================================================

    readme.append(
        "## 🗂️ Problems by Domain"
    )

    readme.append("")


    for category in ordered_categories:

        category_problems = categories[
            category
        ]


        readme.append(
            f"### {category}"
        )

        readme.append("")


        readme.append(
            "| # | Problem | Language | Difficulty |"
        )

        readme.append(
            "|---:|---|---|---|"
        )


        for problem in category_problems:

            number = problem["number"]

            title = problem["title"]

            slug = problem["slug"]

            language = problem["language"]

            difficulty = problem["difficulty"]

            folder = Path(
                problem["folder"]
            )


            relative_folder = (
                folder.as_posix()
            )


            readme.append(

                f"| "
                f"{number if number != 999999 else '-'} | "
                f"[{title}](./{relative_folder}) | "
                f"{language} | "
                f"{difficulty} |"

            )


        readme.append("")


    # ============================================================
    # FOOTER
    # ============================================================

    readme.append("---")

    readme.append("")

    readme.append(
        "🤖 Automatically updated using GitHub Actions."
    )

    readme.append("")

    readme.append(
        "📌 Problems are organized using LeetCode topic tags."
    )


    # ============================================================
    # WRITE README
    # ============================================================

    README_FILE.write_text(
        "\n".join(readme),
        encoding="utf-8"
    )


# ================================================================
# STATS.JSON
# ================================================================

def generate_stats(all_problems):

    easy = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Easy"
    )


    medium = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Medium"
    )


    hard = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Hard"
    )


    unknown = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Unknown"
    )


    total = len(all_problems)


    stats = {

        "totalSolved": total,

        "easy": easy,

        "medium": medium,

        "hard": hard,

        "unknown": unknown,

        "problems": [

            {

                "number": p["number"],

                "title": p["title"],

                "slug": p["slug"],

                "difficulty": p["difficulty"],

                "language": p["language"],

                "tags": p["tags"],

                "primaryDomain": p[
                    "primary_domain"
                ],

                "folder": p[
                    "folder"
                ]

            }

            for p in all_problems

        ]

    }


    STATS_FILE.write_text(

        json.dumps(
            stats,
            indent=2,
            ensure_ascii=False
        ),

        encoding="utf-8"

    )


# ================================================================
# PRINT FINAL RESULT
# ================================================================

def print_summary(all_problems):

    easy = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Easy"
    )


    medium = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Medium"
    )


    hard = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Hard"
    )


    unknown = sum(
        1
        for p in all_problems
        if p["difficulty"] == "Unknown"
    )


    print("")
    print("")
    print("==============================================")
    print("LEETCODE ORGANIZATION COMPLETED")
    print("==============================================")

    print(
        f"Easy          : {easy}"
    )

    print(
        f"Medium        : {medium}"
    )

    print(
        f"Hard          : {hard}"
    )

    print(
        f"Unknown       : {unknown}"
    )

    print(
        f"TOTAL SOLVED  : {len(all_problems)}"
    )

    print("==============================================")
    print("")


    # Domain counts
    domain_counts = {}


    for problem in all_problems:

        domain = problem[
            "primary_domain"
        ]

        domain_counts[domain] = (
            domain_counts.get(domain, 0)
            + 1
        )


    print("DOMAIN COUNTS")
    print("----------------------------------------------")


    for domain in sorted(
        domain_counts
    ):

        print(
            f"{domain:<40} "
            f"{domain_counts[domain]}"
        )


    print("==============================================")
    print("")


# ================================================================
# MAIN
# ================================================================

def main():

    print("")
    print("==============================================")
    print("LEETCODE AUTOMATIC ORGANIZER")
    print("==============================================")
    print("")


    # ------------------------------------------------------------
    # STEP 1
    # Find and collect every problem
    # ------------------------------------------------------------

    problems = collect_problems()


    # ------------------------------------------------------------
    # STEP 2
    # Physically organize folders
    # ------------------------------------------------------------

    organize_all_problems(
        problems
    )


    # ------------------------------------------------------------
    # STEP 3
    # Make sure folder paths are updated
    # ------------------------------------------------------------

    update_folder_paths(
        problems
    )


    # ------------------------------------------------------------
    # STEP 4
    # Sort
    # ------------------------------------------------------------

    all_problems = sort_problems(
        problems
    )


    # ------------------------------------------------------------
    # STEP 5
    # Generate README
    # ------------------------------------------------------------

    generate_readme(
        all_problems
    )


    # ------------------------------------------------------------
    # STEP 6
    # Generate stats.json
    # ------------------------------------------------------------

    generate_stats(
        all_problems
    )


    # ------------------------------------------------------------
    # STEP 7
    # Print result
    # ------------------------------------------------------------

    print_summary(
        all_problems
    )


# ================================================================
# RUN
# ================================================================

if __name__ == "__main__":

    main()
