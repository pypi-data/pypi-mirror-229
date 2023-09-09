from kabu import *

class waves(curves):
 
    """waves is the class from kabuWaves module in the EpidemicKabu library. It is a child class of 
    curves class from module kabu. Its workflow is to identify the cut points that delimites the start
    and the end of a wave using the methods idenCutPointsW() and idenPreviousDatesW(). And filter those cut 
    points according to a threshold with the method idenPreviousDatesW(). A draw of this workflow in https://github.com/LinaMRuizG/EpidemicKabu/tree/main/paper/figures
     """
        
    def __init__(self,dataframe,datesName,casesName,kernel1,kernel2,plotName,dfName,outFolderPlot = "./plots/",outFolderDF="./dataframes/",thresholdW=0):
        
        """The arguments to make an instance are:
         1. dataframe: DataFrame with the dates and the number of cases by date
         2. datesName: Name of the column with the dates which are strings 
         3. casesName: Name of the column with the cases by each date
         4. kernel: value of the parameters to apply the Gaussian kernel.The kernel could be an int or it could be a list with [df,c1,v1,c2],where df is a dataframe with a column c1 with a values v1 and a column c2. In this way you could use a configuration file with the kernels as in https://github.com/LinaMRuizG/EpidemicKabu/blob/main/exampleUseLibrary/data/configurationFile.csv
         5. plotName: The name for the output plot and file of the plot
         6. dfName: The name for the output dataframe. This dataframe has the inital dates and number of cases and it is added a column for the normalized values and smoothed values
         7. outFolderPlot: The directory to put the output plot. The default is ./plots/, be sure of create it
         8. outFolderDF: The directory to put the output dataframe. The default is ./dataframes/, be sure of create it
         9. thresholdW: It is used to filter the waves""" 
        
        super().__init__(dataframe,datesName,casesName,kernel1,kernel2,plotName,dfName,outFolderPlot,outFolderDF)     
        self.thresholdW = thresholdW
    
    
    def idenCutPointsW(self,inputToFindCuts,outputCuts):

        """For a column (i.e.,inputToFindCuts), it identifies the positions (i.e., rows) with a 
        positive value for each consecutive pair of positive-negative values (+/-)."""

        df = self.df

        df[outputCuts]= (df[inputToFindCuts].rolling(2).agg(lambda x : True if x.iloc[0]<0 and x.iloc[1]>0 else False)).fillna(False)
        #puts True to each positive value in inputToFindCuts that is predated by a negative value


    def idenPreviousDatesW(self,inputCuts,inputToFindCuts):

        """Using the columns (i.e.,inputCuts and inputToFindCuts) from the dataframe, it identifies 
        the positions (i.e., rows) with a negative value for each consecutive pair of positive-negative values (+/-)
        or a positive value for each consecutive pair of negative-positive values (-/+). It filters with these positions
        the dates and the values of inputToFindCuts (i.e., the column used to indentify the cut points ***LINK***). 
        Then, it selects the dates associated to the lowest absolute value of each consecutive pair of positive-negative or 
        negative-positive (i.e., ensuring to select the date associate to the value closest to zero or when the values
        of the column cut the axis in the temporal plot ***LINK***)"""

        df = self.df
       
        positions1 = df[df[inputCuts]==True][[self.dN,inputToFindCuts]].reset_index(drop=True)
        #gets the dates and the values in inputToFindCuts which are True in inputCuts (positive values)
       
        positions2 = df[df[self.dN].isin(list(positions1[self.dN] - datetime.timedelta(days=1)))][[self.dN,inputToFindCuts]].reset_index(drop=True)
        #gets the previous dates of dates in position1 (which are the dates of the negative values). Then, it gets their dates and the values in inputToFindCuts 
        positions2.rename(columns={self.dN:self.dN+"1",inputToFindCuts:inputToFindCuts+"1"},inplace=True)
        
        positions = pd.concat([positions1, positions2], axis=1)

        self.cutDatesW = list(positions.agg(lambda x : x[self.dN] if abs(x[inputToFindCuts])<abs(x[inputToFindCuts+"1"])  else x[self.dN+"1"], axis=1))
        #selects the dates associated to the value of inputToFindCuts (in positions) closest to zero

        self.df["cutDatesW"] = self.df[self.dN].isin(self.cutDatesW).astype(int)
        #creates a new column with 1 in the dates selected
        
          
    def thresholdPos(self):

        """It selects those cutDatesW above the threshold"""
        
        thresholdW = self.thresholdW
        df = self.df

        self.cutDatesW = df[df[self.dN].isin(self.cutDatesW)].reset_index(drop = True)
        #selects from df the rows belonging to cutDatesW
        self.cutDatesW = self.cutDatesW.agg(lambda x : x[self.dN] if  x["SecondDerivate"] > thresholdW else [],axis=1)
        #selects the dates in cutDatesW for which the second derivative is higher than the thresholdW
        self.cutDatesW = pd.to_datetime(self.cutDatesW.explode())
        #changes the [] by NaT and puts dates in the correct format 
        self.cutDatesW = self.cutDatesW[~np.isnat(self.cutDatesW)]
        #deletes the NaT dates

        
        self.df["cutDatesW"] = self.df[self.dN].isin(self.cutDatesW).astype(int)
        #creating a column in df with 1 in the cutDays


    def plottingTheCurveNormalized(self,cutDates):

        """It adds the cutDatesW to the temporal plot of the Normalized and Smoothed cases"""
        
        super().plottingTheCurveNormalized()
        
        for date in cutDates:
            plt.axvline(x=date, color='black', linestyle='--', linewidth=.91)
            #adds vertical lines in the cutDays
        plt.savefig(self.outFolderPlot+self.plotName+"N.png")
        plt.close('all')

        
    def plottingTheCurveNoNormalized(self,cutDates):

        """It adds the cutDatesW to the temporal plot of the No-Normalized and Smoothed cases"""
        
        super().plottingTheCurveNoNormalized()
        
        for date in cutDates:
            plt.axvline(x=date, color='black', linestyle='--', linewidth=.91)
        plt.savefig(self.outFolderPlot+self.plotName+"NoN.png")
        plt.close('all')


    def run(self):
       
        """It run all the class methods in the correct order and builds the plot and a dataframe of the plot"""
        
        super().run()
        
        self.idenCutPointsW("FirstDerivateSmoothed","rollingFDS")
        self.idenPreviousDatesW("rollingFDS","FirstDerivateSmoothed")
        #jself.thresholdPos()
        
        
        df = self.df[[self.dN,self.cN,"SmoothedCases","cutDatesW"]]
        df.to_csv(self.outFolderDF + self.dfName + ".csv")

        self.plottingTheCurveNormalized(self.cutDatesW)
        self.plottingTheCurveNoNormalized(self.cutDatesW)

    
