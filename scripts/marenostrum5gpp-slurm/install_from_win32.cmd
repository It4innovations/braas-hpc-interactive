@echo off
REM ######################################################################
REM # This program is free software; you can redistribute it and/or modify
REM # it under the terms of the GNU General Public License as published by
REM # the Free Software Foundation; either version 3 of the License, or
REM # (at your option) any later version.
REM #
REM # This program is distributed in the hope that it will be useful, but
REM # WITHOUT ANY WARRANTY; without even the implied warranty of
REM # MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
REM # General Public License for more details.
REM #
REM # You should have received a copy of the GNU General Public License
REM # along with this program. If not, see <http://www.gnu.org/licenses/>.

REM # (c) IT4Innovations, VSB-TUO
REM ######################################################################

REM Download BlenderPhi 4.5.5 for Linux
echo Downloading BlenderPhi 4.5.5 for Linux...
powershell -Command "Invoke-WebRequest -Uri 'https://code.it4i.cz/raas/blenderphi/-/raw/main/releases/blenderphi-v4.5.5/blenderphi-v4.5.5-karolina-linux-x64-gcc13.tar.xz' -OutFile 'blenderphi.tar.xz'"

REM Transfer BlenderPhi archive to MareNostrum5 cluster
echo Transferring BlenderPhi archive to MareNostrum5...
scp blenderphi.tar.xz MareNostrum5:~/blenderphi.tar.xz

REM Run the Linux installation script
echo Running installation script on MareNostrum5...
ssh MareNostrum5 "if [ -d ~/blenderphi ] ; then rm -rf ~/blenderphi ; fi ; cd ~/ ; tar -xf blenderphi.tar.xz ; rm blenderphi.tar.xz ;"

REM ######################################################################

REM Download braas-hpc-interactive for Linux
echo Downloading braas-hpc-interactive for Linux...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/It4innovations/braas-hpc-interactive/-/archive/main/braas-hpc-interactive-main.tar.gz' -OutFile 'braas-hpc-interactive-main.tar.gz'"

REM Transfer braas-hpc-interactive archive to MareNostrum5 cluster
echo Transferring braas-hpc-interactive archive to MareNostrum5...
scp braas-hpc-interactive-main.tar.gz MareNostrum5:~/braas-hpc-interactive.tar.gz

REM Run the Linux installation script
echo Running installation script on MareNostrum5...
ssh MareNostrum5 "if [ -d ~/braas-hpc-interactive ] ; then rm -rf ~/braas-hpc-interactive ; fi ; cd ~/ ; tar -xf braas-hpc-interactive.tar.gz ; mv braas-hpc-interactive-main ~/braas-hpc-interactive ; rm braas-hpc-interactive.tar.gz ;"

REM ######################################################################
echo Installation completed.
