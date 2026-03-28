# Import pytest, PySpark, transform functions

# Fixture: create local SparkSession for testing

# Test 1: test_flatten_nested_fields
#   Create sample DataFrame with nested owner and license objects
#   Run flatten function
#   Assert owner_login column exists with correct value
#   Assert license_name column exists with correct value

# Test 2: test_deduplication
#   Create DataFrame with two rows sharing the same repo id
#   Run dedup function
#   Assert output has only 1 row

# Test 3: test_null_id_dropped
#   Create DataFrame with one row where id is null
#   Run clean function
#   Assert that row is removed from output

# Test 4: test_type_casting
#   Create DataFrame with stars as string "1500"
#   Run cast function
#   Assert stars column is IntegerType
