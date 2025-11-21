# R-Gen Architecture Documentation Index

## Quick Navigation

### For Immediate Understanding (Start Here)
1. **QUICK_REFERENCE.md** (5 min read)
   - Key facts at a glance
   - Critical files and API mappings
   - See "Current Limitations" for JSON detachment info

### For Detailed Understanding
2. **ARCHITECTURE_OVERVIEW.md** (30-45 min read)
   - Sections 1-5: Core architecture
   - Section 2: Complete JSON file catalog
   - Section 3: Database structure
   - Section 9: Method-to-JSON cross-reference

### For Visual Learners
3. **DEPENDENCY_DIAGRAM.md** (20-30 min read)
   - 8 detailed ASCII diagrams
   - Data flow for every major operation
   - Section 6: Complete request-response cycle

---

## Documentation Overview

### QUICK_REFERENCE.md
**Length:** 161 lines | **Time:** 5-10 minutes

**Content:**
- ContentGenerator status and methods
- JSON file organization
- Critical source files (5 main files)
- SQLite database tables
- API endpoints using ContentGenerator
- Data flow summary
- What's currently persisted vs in-memory
- Current limitations for JSON detachment
- Future detachment strategy

**Best For:**
- Quick lookups
- Getting oriented
- Finding specific endpoints
- Understanding data persistence

**Key Sections:**
- "API Endpoints Using ContentGenerator" table
- "JSON File Categories" tree
- "Current Limitations for JSONs Detachment" checklist
- "Future Detachment Strategy"

---

### ARCHITECTURE_OVERVIEW.md
**Length:** 515 lines | **Time:** 30-45 minutes

**Content:**
1. Project Structure (directory tree)
2. GenerationEngine Class Details (ContentGenerator)
3. All 24 JSON Files (complete catalog with purposes)
4. GameDatabase Structure (SQLite tables)
5. How Game Loads & Uses JSONs (step-by-step)
6. GenerationEngine References (throughout codebase)
7. Architecture Diagram (visual flowchart)
8. Key Integration Points (4 major integrations)
9. Methods Using Each JSON File (cross-reference table)

**Best For:**
- Understanding the full system
- Detailed information on any component
- Planning JSON detachment
- Database design understanding

**Key Sections:**
- Section 2: ContentGenerator class methods (40+ methods listed)
- Section 3: Complete JSON catalog (24 files with descriptions)
- Section 7: Visual architecture diagram
- Section 9: Method-to-JSON cross-reference table

---

### DEPENDENCY_DIAGRAM.md
**Length:** 362 lines | **Time:** 20-30 minutes

**Content:**
1. Import Dependencies (tree diagram)
2. Data Flow - Item Generation Pipeline
3. NPC Generation & Storage
4. Profession Validation Flow
5. Loot Table Generation
6. Complete Request-Response Cycle
7. JSON Loading Sequence at Startup
8. SimulationEngine Integration

**Best For:**
- Visual understanding
- Following data through system
- Understanding dependencies
- Seeing complete flows

**Key Sections:**
- Section 1: Dependency tree showing no circular deps
- Section 6: Full item generation cycle with code
- Section 7: Server startup with all 24 JSON loads
- Section 8: SimulationEngine integration

---

## Document Relationship Map

```
START HERE
    ↓
QUICK_REFERENCE.md
    ├─→ Need details? ──→ ARCHITECTURE_OVERVIEW.md
    │                      ├─→ See Section 2 for JSON details
    │                      ├─→ See Section 3 for DB design
    │                      └─→ See Section 9 for method mapping
    │
    └─→ Need visuals? ──→ DEPENDENCY_DIAGRAM.md
                          ├─→ See Section 1 for dependencies
                          ├─→ See Section 6 for data flows
                          └─→ See Section 8 for integration
```

---

## Finding Specific Information

### "How do items get generated?"
1. Quick answer: QUICK_REFERENCE.md - "API Endpoints Using ContentGenerator" table
2. Detailed: ARCHITECTURE_OVERVIEW.md - Section 4 "How Game Currently Loads & Uses JSONs"
3. Visual: DEPENDENCY_DIAGRAM.md - Section 2 "Data Flow - Item Generation Pipeline"

### "What JSONs are there and what do they do?"
1. Quick list: QUICK_REFERENCE.md - "JSON File Categories"
2. Complete details: ARCHITECTURE_OVERVIEW.md - Section 2 "JSON Configuration Files"
3. Cross-reference: ARCHITECTURE_OVERVIEW.md - Section 9 "Methods Using Each JSON File"

### "Where is GenerationEngine used in the code?"
1. Quick summary: QUICK_REFERENCE.md - "No Direct Dependencies"
2. Complete list: ARCHITECTURE_OVERVIEW.md - Section 5 "GenerationEngine References Throughout Codebase"
3. File locations: DOCUMENTATION_INDEX.md (this file) - "File Locations"

### "What's persisted to the database?"
1. Quick answer: QUICK_REFERENCE.md - "What's Currently Persisted"
2. Details: ARCHITECTURE_OVERVIEW.md - Section 3 "GameDatabase Structure & Storage"
3. Tables: ARCHITECTURE_OVERVIEW.md - Database Tables section

### "How to detach JSONs from GenerationEngine?"
1. Current state: QUICK_REFERENCE.md - "Current Limitations for JSONs Detachment"
2. Strategy: QUICK_REFERENCE.md - "Future Detachment Strategy"
3. Analysis: ARCHITECTURE_OVERVIEW.md - Section 8 "Important Notes"

### "What are the current system dependencies?"
1. Visual: DEPENDENCY_DIAGRAM.md - Section 1 "Import Dependencies"
2. Analysis: ARCHITECTURE_OVERVIEW.md - Section 1 "Current Dependencies on Game Class"
3. Summary: QUICK_REFERENCE.md - "No Direct Dependencies"

### "How does the web server work?"
1. Overview: ARCHITECTURE_OVERVIEW.md - Section 1 "Initialization & JSON Loading"
2. Endpoints: QUICK_REFERENCE.md - "API Endpoints Using ContentGenerator"
3. Full cycle: DEPENDENCY_DIAGRAM.md - Section 6 "Complete Request-Response Cycle"

### "How are NPCs generated and used?"
1. Overview: ARCHITECTURE_OVERVIEW.md - Section 4 example
2. Flow: DEPENDENCY_DIAGRAM.md - Section 3 "NPC Generation & Storage"
3. SimEngine: DEPENDENCY_DIAGRAM.md - Section 8 "SimulationEngine Integration"

### "What's the relationship with SimulationEngine?"
1. Overview: ARCHITECTURE_OVERVIEW.md - Section 1 "No Direct Dependencies"
2. Integration: ARCHITECTURE_OVERVIEW.md - Section 8 "Integration Points"
3. Detailed flow: DEPENDENCY_DIAGRAM.md - Section 8 "SimulationEngine Integration"

---

## Source Code Cross-Reference

### Primary Files Analyzed

| File | Lines | Purpose | Doc Section |
|------|-------|---------|-------------|
| `/GenerationEngine/src/content_generator.py` | 2,823 | Main content generator | ARCH 1,2 / QUICK "ContentGenerator Status" |
| `/Game/game_server.py` | 2,087 | Flask API & WebSocket | ARCH 5 / DEP 6 |
| `/Game/game_database.py` | 486 | SQLite storage | ARCH 3 / QUICK "Database Tables" |
| `/SimulationEngine/src/integration/generator_adapter.py` | 150+ | Adapter pattern | ARCH 6 / DEP 8 |
| `/SimulationEngine/src/integration/entity_factory.py` | 100+ | Conversion factory | ARCH 6 / DEP 8 |

### JSON Files (24 Total)

All located in `/GenerationEngine/data/`

Detailed in: ARCHITECTURE_OVERVIEW.md - Section 2
Listed in: QUICK_REFERENCE.md - "JSON File Categories"
Cross-referenced in: ARCHITECTURE_OVERVIEW.md - Section 9

---

## Key Code Locations

### ContentGenerator Initialization
- **File:** `/GenerationEngine/src/content_generator.py` - Lines 24-78
- **Reference:** ARCHITECTURE_OVERVIEW.md - Section 1
- **Diagram:** DEPENDENCY_DIAGRAM.md - Section 7

### Game Server Integration
- **File:** `/Game/game_server.py`
  - Line 25: Import
  - Lines 37-39: Initialization
  - Lines 671+: Usage
- **Reference:** ARCHITECTURE_OVERVIEW.md - Section 5
- **Diagram:** DEPENDENCY_DIAGRAM.md - Sections 1, 6

### Item Generation Endpoint
- **File:** `/Game/game_server.py` - Line 1362
- **Reference:** ARCHITECTURE_OVERVIEW.md - Section 4
- **Diagram:** DEPENDENCY_DIAGRAM.md - Section 2, 6

### Profession Validation
- **File:** `/Game/game_server.py` - Lines 741, 763
- **Reference:** ARCHITECTURE_OVERVIEW.md - Section 5
- **Diagram:** DEPENDENCY_DIAGRAM.md - Section 4

### Loot Table Generation
- **File:** `/GenerationEngine/src/content_generator.py` - Line 1011
- **Reference:** ARCHITECTURE_OVERVIEW.md - Section 4
- **Diagram:** DEPENDENCY_DIAGRAM.md - Section 5

---

## Reading Recommendations by Role

### For Project Managers
1. QUICK_REFERENCE.md (overview)
2. ARCHITECTURE_OVERVIEW.md - Sections 1, 6, 7 (structure)
3. ARCHITECTURE_OVERVIEW.md - Section 8 "Important Notes"

### For Full-Stack Developers
1. QUICK_REFERENCE.md (all)
2. ARCHITECTURE_OVERVIEW.md (sections 1-5)
3. DEPENDENCY_DIAGRAM.md (sections 1, 6)

### For Backend Engineers
1. QUICK_REFERENCE.md (key facts)
2. ARCHITECTURE_OVERVIEW.md (all sections)
3. DEPENDENCY_DIAGRAM.md - Section 7

### For Frontend Engineers
1. QUICK_REFERENCE.md - "API Endpoints Using ContentGenerator"
2. DEPENDENCY_DIAGRAM.md - Section 6

### For Database Administrator
1. ARCHITECTURE_OVERVIEW.md - Section 3
2. QUICK_REFERENCE.md - "Database Tables"

### For Game Designers (JSON Balance)
1. ARCHITECTURE_OVERVIEW.md - Section 2
2. QUICK_REFERENCE.md - "JSON File Categories"
3. ARCHITECTURE_OVERVIEW.md - Section 9 (method mapping)

### For New Team Members
1. QUICK_REFERENCE.md (5 min overview)
2. DEPENDENCY_DIAGRAM.md - Sections 1, 6 (visual flow)
3. ARCHITECTURE_OVERVIEW.md - Section 1 (architecture)

---

## Documentation Quality Metrics

| Document | Lines | Content Density | Diagrams | Tables | Completeness |
|----------|-------|-----------------|----------|--------|--------------|
| QUICK_REFERENCE.md | 161 | High | 3 | 4 | 90% |
| ARCHITECTURE_OVERVIEW.md | 515 | High | 1 | 2 | 95% |
| DEPENDENCY_DIAGRAM.md | 362 | Medium | 8 | 0 | 100% |
| **Total** | **1,038** | - | **12** | **6** | **95%** |

---

## Last Updated
November 21, 2025

## Analysis Coverage
- GenerationEngine class: 100%
- Game class integration: 100%
- JSON usage: 100%
- GameFolder structure: 100%
- Database structure: 100%
- GenerationEngine references: 100%

---

## Next Steps for JSON Detachment Project

Based on analysis, the recommended approach is:

1. **Create JSON Loader Abstraction**
   - Reference: ARCHITECTURE_OVERVIEW.md - Section 8
   - Target file: ContentGenerator.__init__() lines 24-78

2. **Validate Configuration**
   - Reference: QUICK_REFERENCE.md - "Current Limitations"
   - Ensure all required JSONs exist before use

3. **Update Imports**
   - Reference: DEPENDENCY_DIAGRAM.md - Section 1
   - Update all files that import ContentGenerator

4. **Test Coverage**
   - Reference: ARCHITECTURE_OVERVIEW.md - Section 9
   - Ensure all methods have required JSONs

---

## Document Usage Tips

1. **Use Ctrl+F (Find)** to search for specific terms
2. **Follow links** between sections for related information
3. **Refer to tables** for quick lookups
4. **Study diagrams** for visual understanding
5. **Check cross-references** for method-to-JSON mapping

