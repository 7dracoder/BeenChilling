# Render Environment Variable Update Required

## Critical: Update Supabase Environment Variables

The Supabase client code has been updated to use the correct environment variable names. You need to update your Render environment variables:

### Changes Required

1. **Rename `SUPABASE_KEY`** → **`SUPABASE_ANON_KEY`**
   - This is the public/anonymous key for client-side operations
   - Value: `sb_publishable_ILDq-QK71mkOGpy5j5eMVw_EmrcKLKd`

2. **Rename `SUPABASE_SERVICE_KEY`** → **`SUPABASE_SERVICE_ROLE_KEY`**
   - This is the service role key for backend operations
   - Value: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRnaWdmeHpvemRhdWhkcm92bGZlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ3NzkzNywiZXhwIjoyMDkyMDUzOTM3fQ.GduId4RUDrCGI5hsYUCekGSidQ9zmKJW2YYjWnQ2pd8`

### How to Update on Render

1. Go to your Render dashboard
2. Select your web service
3. Go to "Environment" tab
4. Delete the old variables:
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_KEY`
5. Add the new variables:
   - `SUPABASE_ANON_KEY` = (value from old SUPABASE_KEY)
   - `SUPABASE_SERVICE_ROLE_KEY` = (value from old SUPABASE_SERVICE_KEY)
6. Click "Save Changes"
7. Render will automatically redeploy

### Why This Change?

The old variable names were inconsistent with Supabase's official naming convention. The new names match the standard Supabase environment variable names used in their documentation.

### What Happens After Update?

1. The app will connect to Supabase correctly
2. New simple recipes will be seeded on startup (if not already present)
3. Recipe section will work with single items in the fridge
4. All existing functionality will continue to work

### Verification

After deployment, check the logs for:
```
INFO: Recipes ready.
```

This confirms the recipe seeding completed successfully.
