# Development Workflow & Best Practices

## Feature Development Process

### 1. Branch Strategy
- Create feature branches from `main`: `feature/<feature-name>`
- Use descriptive branch names matching backlog items
- Keep branches focused on single features
- Merge back to main after testing

### 2. Implementation Order
When implementing features, follow this priority:
1. **High Priority** - Features blocking production/demos
2. **Medium Priority** - Enhancements improving UX
3. **Low Priority** - Nice-to-have improvements

### 3. Development Workflow

#### Phase 1: Planning
- Review feature requirements in BACKLOG.md
- Identify affected files and systems
- Check for API dependencies
- Plan testing approach

#### Phase 2: Implementation
- Start with data models if needed (`src/models.py`)
- Implement API integration (`src/sonrai_client.py`)
- Add game logic (entity classes, quest systems)
- Update rendering (`src/renderer.py`)
- Integrate into game engine (`src/game_engine.py`)

#### Phase 3: Testing
- Manual testing in-game
- Test API integration with real Sonrai data
- Verify visual elements render correctly
- Check performance impact
- Test edge cases (no data, API errors, etc.)

#### Phase 4: Documentation
- Update README.md if user-facing
- Add code comments for complex logic
- Update BACKLOG.md to mark completed
- Document any new configuration

### 4. Code Organization Patterns

#### New Quest System
When adding quests (like JIT Access Quest):
1. Create quest class in new file: `src/<quest_name>_quest.py`
2. Follow pattern from `src/service_protection_quest.py`
3. Add quest state to `GameState` in `src/models.py`
4. Integrate quest checks in `src/game_engine.py`
5. Add rendering in `src/renderer.py`

#### New Entity Types
When adding entities (like Auditor, Admin Role):
1. Create entity class in appropriate file or new file
2. Add to entity lists in `GameState`
3. Implement collision detection
4. Add rendering logic
5. Handle interactions in game loop

#### API Integration
When adding Sonrai API calls:
1. Add method to `SonraiAPIClient` in `src/sonrai_client.py`
2. Handle errors gracefully (log, don't crash)
3. Cache results when appropriate
4. Test with real API before committing

### 5. Visual Asset Guidelines

#### Sprite Design
- Maintain 8-bit/16-bit retro aesthetic
- Use consistent color palette
- Keep sprites simple for performance
- Design for 1280x720 base resolution
- Test visibility at different scales

#### Character Design
- Distinct silhouettes for different entity types
- Clear visual indicators (shields, warnings, etc.)
- Consistent size relative to player
- Readable at gameplay distance

### 6. Performance Considerations

#### Always Consider
- Spatial grid for collision detection (already implemented)
- Limit entity counts (MAX_ZOMBIES config)
- Efficient rendering (only visible entities)
- API call throttling/caching
- Frame rate stability (TARGET_FPS)

#### Red Flags
- Nested loops over all entities
- API calls in game loop
- Large sprite files
- Unoptimized collision checks

### 7. Testing Checklist

Before marking feature complete:
- [ ] Feature works in target accounts/levels
- [ ] API integration handles errors
- [ ] Visual elements render correctly
- [ ] No performance degradation
- [ ] Quest resets properly when returning to lobby
- [ ] Success/failure states work
- [ ] Cheat codes still work (if applicable)
- [ ] Save/load preserves feature state

### 8. Common Pitfalls to Avoid

- **Don't** add API calls inside the game loop (60 FPS)
- **Don't** create entities without cleanup logic
- **Don't** hardcode account IDs (use config/API)
- **Don't** skip error handling on API calls
- **Don't** forget to update GameState for new features
- **Don't** break existing quests when adding new ones

### 9. Git Commit Best Practices

- Use descriptive commit messages
- Reference backlog items: "Implement JIT Access Quest (#1)"
- Commit logical units of work
- Test before committing
- Keep commits focused

### 10. Feature Flag Pattern

For experimental features:
```python
# In difficulty_config.py or models.py
ENABLE_JIT_QUEST = True  # Feature flag

# In game logic
if ENABLE_JIT_QUEST and account_is_production:
    # Quest logic
```

## Current Backlog Priority Order

### Immediate (High Priority)
1. **JIT Access Quest** - Production demo requirement
   - Branch: `feature/jit-access-quest`
   - Estimated effort: Medium (2-3 days)
   - Dependencies: Sonrai JIT API endpoints

### Next (Medium Priority)
2. **Improved Raygun Visual** - UX enhancement
   - Branch: `feature/improved-raygun`
   - Estimated effort: Small (4-6 hours)
   - Dependencies: None

## Implementation Roadmap

### Week 1: JIT Access Quest
- Day 1: API integration and data models
- Day 2: Entity classes (Auditor, Admin Role)
- Day 3: Quest logic and rendering
- Day 4: Testing and polish

### Week 2: Raygun Enhancement
- Day 1: Design and implement new raygun sprite
- Day 2: Testing and refinement
