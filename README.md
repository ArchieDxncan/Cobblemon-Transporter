![Cobblemon Transporter Logo](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobblemontransporter.png) <!-- Replace with the path to your logo -->

![GitHub License](https://img.shields.io/github/license/ArchieDxncan/Cobblemon-Transporter?color=blue)  
![GitHub Release](https://img.shields.io/github/v/release/ArchieDxncan/Cobblemon-Transporter?include_prereleases)  
![GitHub Issues](https://img.shields.io/github/issues/ArchieDxncan/Cobblemon-Transporter)  

## Overview
Cobblemon Transporter is THE tool that bridges the gap between Pokémon and Minecraft. Allowing Pokémon to travel both ways. 

[Please consider using my Cobblemon sidemod if you aren't already, it allows you to import more data such Met Date and Met Level!](https://www.curseforge.com/minecraft/mc-mods/cobblemon-extra-data)

---

## Screenshots

![Screenshot 1](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobblenew.PNG)

Converted Cobblemon are not classed as legal. Please use my fork of [ALM](https://github.com/ArchieDxncan/PKHeX-Plugins) if you would like to transfer into HOME or use a trade bot. It isn't perfect but most Pokémon should be able to legalise. For the best results please try to legalise a Pokémon in a game they are easily obtainable in.

<details>
<summary>Talonflame (Angry Bird)</summary>

- **Original Game**  
  ![Screenshot 2](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobble2.png)  

- **Exported to SV**  
  ![Screenshot 3](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobble3.PNG)  

</details>

<details>
<summary>Alolan-Dugtrio</summary>

- **Original Game**  
  ![Screenshot 4](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobble4.PNG)  

- **Exported to USUM**  
  ![Screenshot 5](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobble5.png)  

</details>

---

## Capabilities

- **Save File Integration**:  Import and export Pokémon between Cobblemon and your game saves.
- **User-Friendly Interface**: Designed to be simple and intuitive for users of all skill levels.
- **Pokémon Home/Bank Experience**: All imported Pokémon are stored in a nice UI for viewing.

---

## Instructions

### Installation
1. [Download the latest release](https://github.com/ArchieDxncan/cobblemon-transporter/releases/) or download most recent from source.
2. Ensure you have Python installed on your system. (Downloading from Windows Store automatically adds to PATH)
3. Run dependencies.bat to install the required dependencies.

---

### Usage
- Cobblemon save files are stored in your world folder at pokemon/playerpartystore and pokemon/pcstore under your Minecraft UUID.
- There is a help section on the toolbar. Either post an issue or message me on Discord @miniduncan if you need help!
1. Launch the tool by running start.bat
3. Use the file dropdown to import from either Pokémon or Cobblemon.
4. Import .dat files for Cobblemon or .pk files for Pokémon.
5. The selected Pokémon will be imported into the Cobblemon folder as .json files. (Errors may occur as I haven't tested every single move/ability)
6. Export Pokémon to Cobblemon. Note: Ensure you have a Pokemon in the .dat you are exporting to.
5. Export Cobblemon to Pokémon. Note: You can use PKHeX to either import into your save file, then legalise the Pokémon using [ALM](https://github.com/architdate/PKHeX-Plugins)

Cobblemon -> Pokémon will be exported as .cb9 (equivalent to .pk9) you can enable AllowIncompatibleConversion in PKHeX settings to transfer to pre Gen 9.
It is recommended to return a Pokémon to the game it was imported from otherwise values such as met location break.

---

## Diagram

![Cobblemon Transporter Diagram](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobblemontransporterdiagram.png)

---

## Contributing

If you'd like to contribute to the Cobblemon Transporter, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---
