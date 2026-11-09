# Samples

The `.evtx` files in this folder come from the
[EVTX-ATTACK-SAMPLES](https://github.com/sbousseaden/EVTX-ATTACK-SAMPLES)
repository by Samir Bousseaden, and are distributed under the
GNU General Public License (see `LICENSE` in this folder).

They are used here only to test the Sigma rules of this project.
The rules themselves are not covered by this license.

## Chainsaw Tests
> My chainsaw executable is in the ./chainsaw/target/realease/ folder

```
./chainsaw hunt <FileToAnalyze_Path> -s <RuleFileYML_Path> --mapping <MappingFileYML_Path>
```
