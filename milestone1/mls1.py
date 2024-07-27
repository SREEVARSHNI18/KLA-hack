import pandas as pd
import numpy as np

def calculate_area(xmin, xmax, ymin, ymax):
    """Calculate the area of a rectangle given its coordinates."""
    return (xmax - xmin) * (ymax - ymin)

def get_overlap_area(care_area, main_field):
    """Calculate the overlapping area between a care area and a main field."""
    x_min_overlap = max(care_area["Xmin"], main_field["Xmin"])
    x_max_overlap = min(care_area["Xmax"], main_field["Xmax"])
    y_min_overlap = max(care_area["Ymin"], main_field["Ymin"])
    y_max_overlap = min(care_area["Ymax"], main_field["Ymax"])
    
    if x_min_overlap < x_max_overlap and y_min_overlap < y_max_overlap:
        overlap_area = calculate_area(x_min_overlap, x_max_overlap, y_min_overlap, y_max_overlap)
        return overlap_area, {
            "Xmin": x_min_overlap,
            "Xmax": x_max_overlap,
            "Ymin": y_min_overlap,
            "Ymax": y_max_overlap
        }
    else:
        return 0, None

def calculate_diagonal(size):
    """Calculate the diagonal length of a square given its side length."""
    return np.sqrt(2) * size

def create_main_fields_around_care_areas(care_areas_df, main_field_size):
    """Generate main fields centered around each care area based on its diagonal."""
    main_fields = []
    main_field_id = 0
    
    for _, care_area in care_areas_df.iterrows():
        x_center = (care_area["Xmin"] + care_area["Xmax"]) / 2
        y_center = (care_area["Ymin"] + care_area["Ymax"]) / 2
        diagonal = calculate_diagonal(care_area["Xmax"] - care_area["Xmin"])
        
        # Use the diagonal to define the size of the main field
        size = max(main_field_size, diagonal)
        half_size = size / 2
        
        main_field = {
            "ID": main_field_id,
            "Xmin": x_center - half_size,
            "Xmax": x_center + half_size,
            "Ymin": y_center - half_size,
            "Ymax": y_center + half_size
        }
        main_fields.append(main_field)
        main_field_id += 1
    
    return pd.DataFrame(main_fields)

def create_subfields(care_areas_df, main_fields_df, sub_field_size):
    """Generate subfields within overlapping areas between care areas and main fields."""
    sub_fields = []
    subfield_id = 0
    
    for _, care_area in care_areas_df.iterrows():
        main_field = find_main_field_for_care_area(care_area, main_fields_df)
        if main_field is not None:
            overlap_area, overlap_rect = get_overlap_area(care_area, main_field)
            if overlap_area > 0:
                # Calculate subfields within the overlapping area
                sub_x_min, sub_y_min = overlap_rect["Xmin"], overlap_rect["Ymin"]
                sub_x_max, sub_y_max = overlap_rect["Xmax"], overlap_rect["Ymax"]
                
                # Calculate the number of subfields needed in each dimension
                num_x_subfields = int(np.ceil((sub_x_max - sub_x_min) / sub_field_size))
                num_y_subfields = int(np.ceil((sub_y_max - sub_y_min) / sub_field_size))
                
                for i in range(num_x_subfields):
                    for j in range(num_y_subfields):
                        sub_x = sub_x_min + i * sub_field_size
                        sub_y = sub_y_min + j * sub_field_size
                        
                        # Ensure subfield size is consistent and covers the area completely
                        sub_x_max_actual = sub_x + sub_field_size
                        sub_y_max_actual = sub_y + sub_field_size
                        
                        # Create subfields with proper coverage
                        sub_field = {
                            "ID": subfield_id,  # Unique ID for each subfield
                            "Xmin": sub_x,
                            "Xmax": sub_x_max_actual,
                            "Ymin": sub_y,
                            "Ymax": sub_y_max_actual,
                            "Main Field ID": int(main_field['ID'])
                        }
                        sub_fields.append(sub_field)
                        subfield_id += 1
    return pd.DataFrame(sub_fields)

def find_main_field_for_care_area(care_area, main_fields_df):
    """Find the main field that intersects with a given care area."""
    for _, main_field in main_fields_df.iterrows():
        overlap_area, _ = get_overlap_area(care_area, main_field)
        if overlap_area > 0:
            return main_field
    return None

def main():
    # Load the care areas CSV file
    care_areas_file_path = r"C:\Users\sreev\OneDrive\Desktop\college\kla_hack\Dataset-0\Dataset-0\1st\CareAreas.csv"
    care_areas_df = pd.read_csv(care_areas_file_path, names=["ID", "Xmin", "Xmax", "Ymin", "Ymax"])

    # Load the metadata CSV file
    metadata_file_path = r"C:\Users\sreev\OneDrive\Desktop\college\kla_hack\Dataset-0\Dataset-0\1st\metadata.csv"
    metadata_df = pd.read_csv(metadata_file_path)

    # Extract main field size and subfield size from metadata
    main_field_size = metadata_df.iloc[0]["Main Field Size"]
    sub_field_size = metadata_df.iloc[0]["Sub Field size"]

    # Create main fields centered around care areas
    main_fields_df = create_main_fields_around_care_areas(care_areas_df, main_field_size)

    # Create subfields
    sub_fields_df = create_subfields(care_areas_df, main_fields_df, sub_field_size)

    # Ensure IDs are integers
    main_fields_df["ID"] = main_fields_df["ID"].astype(int)
    sub_fields_df["ID"] = sub_fields_df["ID"].astype(int)
    sub_fields_df["Main Field ID"] = sub_fields_df["Main Field ID"].astype(int)
    care_areas_df["ID"] = care_areas_df["ID"].astype(int)

    # Save DataFrames to CSV files
    main_field_output_path = r"C:\Users\sreev\OneDrive\Desktop\college\kla_hack\Dataset-0\MainFields.csv"
    main_fields_df.to_csv(main_field_output_path, header=False, index=False)

    sub_field_output_path = r"C:\Users\sreev\OneDrive\Desktop\college\kla_hack\Dataset-0\SubFields.csv"
    sub_fields_df.to_csv(sub_field_output_path, header=False, index=False)

    # Print the resulting DataFrames
    print("Main Fields DataFrame:")
    print(main_fields_df)
    print("\nSub Fields DataFrame:")
    print(sub_fields_df)
    

if __name__ == "__main__":
    main()
