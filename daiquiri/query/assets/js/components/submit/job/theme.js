import { IThemeProvider, SciChartJsNavyTheme } from "scichart";

export class SciChart2022AppTheme {
    constructor() {
        // Instantiate the SciChart theme object
        this.SciChartJsTheme = new SciChartJsNavyTheme();

        // General colors
        this.ForegroundColor = "#FFFFFF";
        this.Background = this.SciChartJsTheme.sciChartBackground;

        // Series colors
        this.VividSkyBlue = "#50C7E0";
        this.VividPink = "#EC0F6C";
        this.VividTeal = "#30BC9A";
        this.VividOrange = "#F48420";
        this.VividBlue = "#364BA0";
        this.VividPurple = "#882B91";
        this.VividGreen = "#67BDAF";
        this.VividRed = "#C52E60";

        this.DarkIndigo = "#14233C";
        this.Indigo = "#264B93";

        this.MutedSkyBlue = "#83D2F5";
        this.MutedPink = "#DF69A8";
        this.MutedTeal = "#7BCAAB";
        this.MutedOrange = "#E7C565";
        this.MutedBlue = "#537ABD";
        this.MutedPurple = "#A16DAE";
        this.MutedRed = "#DC7969";

        this.PaleSkyBlue = "#E4F5FC";
        this.PalePink = "#EEB3D2";
        this.PaleTeal = "#B9E0D4";
        this.PaleOrange = "#F1CFB5";
        this.PaleBlue = "#B5BEDF";
        this.PalePurple = "#CFB4D5";
    }
}

// Create and export an instance of the theme class
export const appTheme = new SciChart2022AppTheme();
