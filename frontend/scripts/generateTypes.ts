import { createClient } from '@supabase/supabase-js'

const projectUrl = 'https://usdzfxisjnczvgijxmlt.supabase.co'
const anonKey = 'your_anon_key_here' // From Supabase settings

const supabase = createClient(projectUrl, anonKey)

async function generateTypes() {
  try {
    // Fetch schema information
    const { data, error } = await supabase.rpc('get_schema_info')
    if (error) throw error
    
    console.log('Schema generated successfully')
    console.log(JSON.stringify(data, null, 2))
  } catch (err) {
    console.error('Error:', err)
  }
}

generateTypes()