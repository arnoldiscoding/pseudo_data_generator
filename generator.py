from datetime import datetime
import sys, argparse, csv, re, random, string

parser = argparse.ArgumentParser(
    prog='Generator',
    description='generate pseudo data for sql tables',
)

parser.add_argument("--rows")
parser.add_argument("--input")
parser.add_argument("--output")
args = parser.parse_args()

def preprocess_file(filename: str) -> str:
    """
    This function turns the content of the file into a one liner as text
    """

    result_string = ""

    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            result_string += line.strip()
    
    return result_string

def generate_int(digits: int):
    return random.randint(1, 10**digits - 1)

def generate_tinyint():
    return random.randint(0, 1)

def generate_double(min_value=1.0, max_value=1000.0):
    return random.uniform(min_value, max_value)

def generate_longtext(min_length = 1, max_length = 10):
    length = random.randint(min_length, max_length)
    characters = string.ascii_letters + string.digits # + string.punctuation
    random_string = ''.join(random.choice(characters) for _ in range(length))
    
    return random_string 

def generate_random_datetime(start_date=datetime(2024, 1, 1), end_date=datetime(2026, 1, 1)):
    # Generate a random timestamp between the start and end dates
    random_timestamp = random.uniform(start_date.timestamp(), end_date.timestamp())
    return datetime.fromtimestamp(random_timestamp).strftime("%Y-%m-%d %H:%M:%S")

def generate_item_by_instruction(keywords: tuple):
    """
    Given the header description query
    Return a random datum of that type
    """
    if 'tinyint' in keywords[1]:
        result = generate_tinyint()
        return result
    elif 'int' in keywords[1]:
        groups = re.search(r'\w*\((\d*)\)', keywords[1])
        return generate_int(int(groups[1]))
    elif 'text' in keywords[1]:
        return generate_longtext()
    elif 'datetime' in keywords[1]:
        return generate_random_datetime()
    elif 'double' in keywords[1]:
        return generate_double()
    elif 'primary' in keywords[0].lower() or 'constraint' in keywords[0].lower():
        return None
    else:
        raise ValueError(f"failed to identify data type for this field {keywords[0]}")
    
def get_instruction_template(field_string):
    keywords = field_string.strip().split()
    return (keywords[0], keywords[1])

def raw_query_parser(raw_query: str):
    """
    Given a raw query as string,
    Return a instruction template
    """
    groups = re.search(r'(CREATE\s*TABLE\s*\w*)\s*\((.*)\)', raw_query, re.IGNORECASE)
    create_table_string = groups[1]
    raw_headers = groups[2]
    
    # Table Name
    table_name = re.search(r'(CREATE\s*TABLE\s*)(\w*)', create_table_string)[2]

    # Different Header
    headers = raw_headers.split(',')
    instructions = []
    for header in headers:
        result = get_instruction_template(header)
        if 'primary' in result[0].lower() or 'constraint' in result[0].lower():
            continue
        else:
            instructions.append(result)

    return table_name, instructions

def generate_data(instructions: list, iterations: int):
    """
    Given some sort of instruction template that specifies format
    Return a list of pseudo data
    """
    result = list()
    for i in range(iterations):
        new_data = list()
        for instruction in instructions:
            pseudo_data = generate_item_by_instruction(instruction)
            if pseudo_data != None:
                new_data.append(pseudo_data)
        result.append(new_data)
    return result

def create_csv_from_data(output_filename, field, data):
    with open(output_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(field)
        writer.writerows(data)

def main():
    raw_query = preprocess_file(args.input)
    table_name, instructions = raw_query_parser(raw_query)
    data = generate_data(instructions, int(args.rows))
    create_csv_from_data(args.output, [tup[0] for tup in instructions], data)

if __name__ == "__main__":
    main()