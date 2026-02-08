#!/bin/bash

# Build React app for production
cd frontend
npm run build
cd ..

# Output will be in frontend/dist/
echo "✅ Frontend build complete. Ready for deployment."
