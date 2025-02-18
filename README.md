![Cobblemon Transporter Logo](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobblemontransporter.png) <!-- Replace with the path to your logo -->

## Overview
Cobblemon Transporter is THE tool that bridges the gap between Pokémon and Minecraft. Allowing Pokémon to travel both ways. 


---

## Screenshots

PC MENU
![Screenshot 1](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobble1.PNG) 

Shown Pokémon are not classed as legal. [ALM](https://github.com/architdate/PKHeX-Plugins) would be needed if you want to store in Pokémon Home or trade to a real console using SysBot.
Talonflame (Angry Bird) in original game
![Screenshot 2](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobble2.png) #
Talonflame (Angry Bird) exported to SV
![Screenshot 3](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobble3.PNG) 

Alolan-Dugtrio in original game
![Screenshot 4](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobble4.PNG) 
Alolan-Dugtrio exported to USUM
![Screenshot 5](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/cobble5.png) 
---

## Capabilities

- **Save File Integration**:  Import and export Pokémon between Cobblemon and your game saves.
- **User-Friendly Interface**: Designed to be simple and intuitive for users of all skill levels.
- **Pokémon Home/Bank Experience**: All imported Pokémon are stored in a nice UI for viewing.

---

## Limitations

Due to the constraints of Cobblemon's data structure, Pokémon exported to Cobblemon will not retain the following details:
 - Movesets
 - OT (Original Trainer)
 - Met Date, Location
 - Origin Game
 - PID, TID, SID
 - Ribbons

---

## Instructions

### Installation
1. [Download the latest release](https://github.com/ArchieDxncan/cobblemon-transporter/releases/) or download most recent from source.
2. Ensure you have Python installed on your system.
3. Run dependencies.bat to install the required dependencies.

---

### Usage
1. Launch the tool by running start.bat
2. Use the file dropdown to import from either Pokémon or Cobblemon.
3. Import .nbt files for Cobblemon or .pb8/.pk9 files for Pokémon.
4. The selected Pokémon will be imported into the Cobblemon folder as .json files. (Errors may occur as I haven't tested every single move/ability)
5. Export Pokémon to Cobblemon. Note: Exporting is a one-by-one process and will overwrite the Pokémon in the chosen slot.
5. Export Cobblemon to Pokémon. Note: You can use PKHeX to either import into your save file and legalise the Pokémon using [ALM](https://github.com/architdate/PKHeX-Plugins)

Cobblemon -> Pokémon will be exported as .cb9 (equivalent to .pk9) you can enable AllowIncompatibleConversion in PKHeX settings to import to pre Gen 9.

---

## Diagram

![Cobblemon Transporter Diagram](https://github.com/ArchieDxncan/cobblemon-transporter/blob/main/Images/transporter.png)

---

## Contributing

If you'd like to contribute to the Cobblemon Transporter, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---
