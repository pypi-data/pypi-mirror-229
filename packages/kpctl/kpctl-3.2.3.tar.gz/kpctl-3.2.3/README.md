kpctl
=====

Command line interface to:

- inspect, document, enhance and validate BPMN files; and
- execute process-based applications on the KnowProcess platform

Build and publish to PyPI
-----------------------------------------

1. Increment version

   ```
   bumpversion --current-version 3.2.2 [major|minor|patch] pyproject.toml
   ```

2. Build...

   ```
   poetry build
   ```

3. Publish to production server (cannot be repeated for same version)

   ```
   poetry publish --build
   ```
