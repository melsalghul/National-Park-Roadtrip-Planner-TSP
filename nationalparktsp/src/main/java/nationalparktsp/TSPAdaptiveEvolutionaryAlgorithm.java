package nationalparktsp;

import org.cicirello.permutations.Permutation;
import org.cicirello.search.Configurator;
import org.cicirello.search.SolutionCostPair;
import org.cicirello.search.evo.AdaptiveEvolutionaryAlgorithm;
import org.cicirello.search.evo.FitnessProportionalSelection;
import org.cicirello.search.evo.InverseCostFitnessFunction;
import org.cicirello.search.operators.permutations.EnhancedEdgeRecombination;
import org.cicirello.search.operators.permutations.PermutationInitializer;
import org.cicirello.search.operators.permutations.ReversalMutation;
import org.cicirello.search.problems.tsp.RandomTSPMatrix;

import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvValidationException;

import java.io.FileReader;
import java.io.IOException;

public final class TSPAdaptiveEvolutionaryAlgorithm {


    public static void main(String[] args) throws IOException, CsvValidationException {
       
        Configurator.configureRandomGenerator(101);
       
        // load matrix from CSV file
        String filename = "DataScraping\\drivableDistanceMatrix.csv";
        
        double[][] distanceMatrix = loadMatrix(filename);

        int numCities = 51;
        
        RandomTSPMatrix.Double problem = new RandomTSPMatrix.Double(distanceMatrix);

        int populationSize = 100;
        int maxGenerations = 1000;
        int numElite = 10;
        

        //run adaptive evolutionary algorithm
        AdaptiveEvolutionaryAlgorithm<Permutation> aea =
            new AdaptiveEvolutionaryAlgorithm<Permutation>(
                populationSize,
                new ReversalMutation(),
                new EnhancedEdgeRecombination(),
                new PermutationInitializer(numCities),
                new InverseCostFitnessFunction<Permutation>(problem),
                new FitnessProportionalSelection(),
                numElite);
        
        SolutionCostPair<Permutation> solution =
            aea.optimize(maxGenerations);
    
        System.out.println("Best tour length: " + solution.getCost());
        System.out.println("Permutation:      " + solution.getSolution());
    }    

    private static double[][] loadMatrix(String filename) throws IOException, CsvValidationException{
        //number of parks
        int size = 51;
        double[][] matrix = new double[size][size];

        //read from csv
        try (CSVReader reader = new CSVReader(new FileReader(filename))) {
            String[] row;
            reader.readNext(); // skip header row
            int i = 0;
            while ((row = reader.readNext()) != null && i < size) {
                for (int j = 0; j < size; j++) {
                    // skip first column (park name)
                    matrix[i][j] = Math.round(Double.parseDouble(row[j+1]) * 10000.0) / 10000.0;
                }
                i++;
            }
        }

        return matrix;
    }


}





