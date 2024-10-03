import * as THREE from "three";

export function createOrigin(scene, thickness=0.03, length=50, opacity=0.4) {


    let geometry = new THREE.BoxGeometry(length, thickness, thickness);
    let material = new THREE.MeshBasicMaterial({color: 0xff0000, transparent: true, opacity: opacity});
    const XAXIS = new THREE.Mesh(geometry, material);
    scene.add(XAXIS); // RED
    
    geometry = new THREE.BoxGeometry(thickness, length, thickness);
    material = new THREE.MeshBasicMaterial({color: 0x0000ff, transparent: true, opacity: opacity});
    const YAXIS = new THREE.Mesh(geometry, material);
    scene.add(YAXIS); // GREEN
    
    geometry = new THREE.BoxGeometry(thickness, thickness, length);
    material = new THREE.MeshBasicMaterial({color: 0x00ff00, transparent: true, opacity: opacity});
    const ZAXIS = new THREE.Mesh(geometry, material);
    scene.add(ZAXIS); // BLUE


}