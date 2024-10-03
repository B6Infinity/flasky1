export function gazeboCoords2THREE(coords){
    // In Gazebo, z-axis is upward, but in 3js, y-axis is upward. This function will take in gazebo coordinates and change them for z axis to appear upward
    
    // SWAPS Z and Y axes

    return [coords[0], coords[2], coords[1]];

}